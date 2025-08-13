/**
 * MLOps Experiment Tracker - MLOps Episode 44
 * Production-ready experiment tracking and management system
 * 
 * Author: Claude Code
 * Context: Comprehensive experiment tracking system for ML model development
 */

package com.episode44.mlops;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.io.*;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.sql.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.type.TypeReference;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Production MLOps Experiment Tracking System
 * Mumbai me sabse comprehensive experiment tracking!
 */
public class MLOpsExperimentTracker {
    
    private static final Logger logger = LoggerFactory.getLogger(MLOpsExperimentTracker.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final DateTimeFormatter TIMESTAMP_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    
    private final String dbPath;
    private final String artifactsPath;
    private final ExecutorService executor;
    private final AtomicLong experimentCounter = new AtomicLong(0);
    
    // Experiment registry
    private final Map<String, ExperimentRun> activeExperiments = new ConcurrentHashMap<>();
    
    /**
     * Experiment run metadata
     */
    public static class ExperimentRun {
        @JsonProperty("experiment_id")
        private String experimentId;
        
        @JsonProperty("experiment_name")
        private String experimentName;
        
        @JsonProperty("description")
        private String description;
        
        @JsonProperty("user_id")
        private String userId;
        
        @JsonProperty("project_name")
        private String projectName;
        
        @JsonProperty("status")
        private ExperimentStatus status;
        
        @JsonProperty("start_time")
        private LocalDateTime startTime;
        
        @JsonProperty("end_time")
        private LocalDateTime endTime;
        
        @JsonProperty("parameters")
        private Map<String, Object> parameters;
        
        @JsonProperty("metrics")
        private Map<String, Object> metrics;
        
        @JsonProperty("tags")
        private Set<String> tags;
        
        @JsonProperty("artifacts")
        private Map<String, String> artifacts;
        
        @JsonProperty("model_checkpoints")
        private List<ModelCheckpoint> modelCheckpoints;
        
        @JsonProperty("hardware_info")
        private HardwareInfo hardwareInfo;
        
        @JsonProperty("git_commit")
        private String gitCommit;
        
        @JsonProperty("dependencies")
        private Map<String, String> dependencies;
        
        @JsonProperty("dataset_info")
        private DatasetInfo datasetInfo;
        
        // Constructors, getters, setters
        public ExperimentRun() {
            this.parameters = new HashMap<>();
            this.metrics = new HashMap<>();
            this.tags = new HashSet<>();
            this.artifacts = new HashMap<>();
            this.modelCheckpoints = new ArrayList<>();
            this.dependencies = new HashMap<>();
            this.status = ExperimentStatus.RUNNING;
            this.startTime = LocalDateTime.now();
        }
        
        public ExperimentRun(String experimentId, String experimentName, String userId, String projectName) {
            this();
            this.experimentId = experimentId;
            this.experimentName = experimentName;
            this.userId = userId;
            this.projectName = projectName;
        }
        
        // Getters and setters
        public String getExperimentId() { return experimentId; }
        public void setExperimentId(String experimentId) { this.experimentId = experimentId; }
        
        public String getExperimentName() { return experimentName; }
        public void setExperimentName(String experimentName) { this.experimentName = experimentName; }
        
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        
        public String getUserId() { return userId; }
        public void setUserId(String userId) { this.userId = userId; }
        
        public String getProjectName() { return projectName; }
        public void setProjectName(String projectName) { this.projectName = projectName; }
        
        public ExperimentStatus getStatus() { return status; }
        public void setStatus(ExperimentStatus status) { this.status = status; }
        
        public LocalDateTime getStartTime() { return startTime; }
        public void setStartTime(LocalDateTime startTime) { this.startTime = startTime; }
        
        public LocalDateTime getEndTime() { return endTime; }
        public void setEndTime(LocalDateTime endTime) { this.endTime = endTime; }
        
        public Map<String, Object> getParameters() { return parameters; }
        public void setParameters(Map<String, Object> parameters) { this.parameters = parameters; }
        
        public Map<String, Object> getMetrics() { return metrics; }
        public void setMetrics(Map<String, Object> metrics) { this.metrics = metrics; }
        
        public Set<String> getTags() { return tags; }
        public void setTags(Set<String> tags) { this.tags = tags; }
        
        public Map<String, String> getArtifacts() { return artifacts; }
        public void setArtifacts(Map<String, String> artifacts) { this.artifacts = artifacts; }
        
        public List<ModelCheckpoint> getModelCheckpoints() { return modelCheckpoints; }
        public void setModelCheckpoints(List<ModelCheckpoint> modelCheckpoints) { this.modelCheckpoints = modelCheckpoints; }
    }
    
    /**
     * Experiment status enumeration
     */
    public enum ExperimentStatus {
        RUNNING, COMPLETED, FAILED, CANCELLED
    }
    
    /**
     * Model checkpoint information
     */
    public static class ModelCheckpoint {
        @JsonProperty("checkpoint_id")
        private String checkpointId;
        
        @JsonProperty("epoch")
        private int epoch;
        
        @JsonProperty("step")
        private long step;
        
        @JsonProperty("metrics")
        private Map<String, Double> metrics;
        
        @JsonProperty("model_path")
        private String modelPath;
        
        @JsonProperty("timestamp")
        private LocalDateTime timestamp;
        
        @JsonProperty("is_best")
        private boolean isBest;
        
        public ModelCheckpoint() {}
        
        public ModelCheckpoint(String checkpointId, int epoch, long step, Map<String, Double> metrics, String modelPath) {
            this.checkpointId = checkpointId;
            this.epoch = epoch;
            this.step = step;
            this.metrics = metrics;
            this.modelPath = modelPath;
            this.timestamp = LocalDateTime.now();
            this.isBest = false;
        }
        
        // Getters and setters
        public String getCheckpointId() { return checkpointId; }
        public void setCheckpointId(String checkpointId) { this.checkpointId = checkpointId; }
        
        public int getEpoch() { return epoch; }
        public void setEpoch(int epoch) { this.epoch = epoch; }
        
        public long getStep() { return step; }
        public void setStep(long step) { this.step = step; }
        
        public Map<String, Double> getMetrics() { return metrics; }
        public void setMetrics(Map<String, Double> metrics) { this.metrics = metrics; }
        
        public String getModelPath() { return modelPath; }
        public void setModelPath(String modelPath) { this.modelPath = modelPath; }
        
        public boolean isBest() { return isBest; }
        public void setBest(boolean best) { isBest = best; }
    }
    
    /**
     * Hardware information
     */
    public static class HardwareInfo {
        @JsonProperty("cpu_info")
        private String cpuInfo;
        
        @JsonProperty("memory_gb")
        private double memoryGb;
        
        @JsonProperty("gpu_info")
        private List<String> gpuInfo;
        
        @JsonProperty("os_info")
        private String osInfo;
        
        @JsonProperty("python_version")
        private String pythonVersion;
        
        public HardwareInfo() {
            this.gpuInfo = new ArrayList<>();
            // Collect system info
            collectSystemInfo();
        }
        
        private void collectSystemInfo() {
            Runtime runtime = Runtime.getRuntime();
            this.memoryGb = runtime.maxMemory() / (1024.0 * 1024.0 * 1024.0);
            this.osInfo = System.getProperty("os.name") + " " + System.getProperty("os.version");
            this.cpuInfo = System.getProperty("os.arch") + " (" + runtime.availableProcessors() + " cores)";
            
            // Simulate GPU detection (in production, use actual GPU detection libraries)
            if (new Random().nextBoolean()) {
                this.gpuInfo.add("NVIDIA RTX 3080 (10GB)");
            }
        }
        
        // Getters and setters
        public String getCpuInfo() { return cpuInfo; }
        public double getMemoryGb() { return memoryGb; }
        public List<String> getGpuInfo() { return gpuInfo; }
        public String getOsInfo() { return osInfo; }
    }
    
    /**
     * Dataset information
     */
    public static class DatasetInfo {
        @JsonProperty("dataset_name")
        private String datasetName;
        
        @JsonProperty("dataset_version")
        private String datasetVersion;
        
        @JsonProperty("dataset_path")
        private String datasetPath;
        
        @JsonProperty("dataset_size")
        private long datasetSize;
        
        @JsonProperty("num_samples")
        private long numSamples;
        
        @JsonProperty("num_features")
        private int numFeatures;
        
        @JsonProperty("data_hash")
        private String dataHash;
        
        public DatasetInfo() {}
        
        public DatasetInfo(String datasetName, String datasetVersion, String datasetPath, 
                          long numSamples, int numFeatures) {
            this.datasetName = datasetName;
            this.datasetVersion = datasetVersion;
            this.datasetPath = datasetPath;
            this.numSamples = numSamples;
            this.numFeatures = numFeatures;
            this.dataHash = generateDataHash();
        }
        
        private String generateDataHash() {
            // Simulate data hash generation
            return "sha256:" + UUID.randomUUID().toString().replace("-", "").substring(0, 16);
        }
        
        // Getters and setters
        public String getDatasetName() { return datasetName; }
        public void setDatasetName(String datasetName) { this.datasetName = datasetName; }
        
        public String getDatasetVersion() { return datasetVersion; }
        public void setDatasetVersion(String datasetVersion) { this.datasetVersion = datasetVersion; }
        
        public long getNumSamples() { return numSamples; }
        public void setNumSamples(long numSamples) { this.numSamples = numSamples; }
        
        public int getNumFeatures() { return numFeatures; }
        public void setNumFeatures(int numFeatures) { this.numFeatures = numFeatures; }
    }
    
    /**
     * Experiment comparison result
     */
    public static class ExperimentComparison {
        @JsonProperty("experiments")
        private List<ExperimentRun> experiments;
        
        @JsonProperty("common_parameters")
        private Map<String, Object> commonParameters;
        
        @JsonProperty("different_parameters")
        private Map<String, Map<String, Object>> differentParameters;
        
        @JsonProperty("metric_comparison")
        private Map<String, Map<String, Object>> metricComparison;
        
        @JsonProperty("best_experiment")
        private String bestExperiment;
        
        @JsonProperty("comparison_metric")
        private String comparisonMetric;
        
        public ExperimentComparison() {
            this.experiments = new ArrayList<>();
            this.commonParameters = new HashMap<>();
            this.differentParameters = new HashMap<>();
            this.metricComparison = new HashMap<>();
        }
        
        // Getters and setters
        public List<ExperimentRun> getExperiments() { return experiments; }
        public Map<String, Object> getCommonParameters() { return commonParameters; }
        public Map<String, Map<String, Object>> getDifferentParameters() { return differentParameters; }
        public Map<String, Map<String, Object>> getMetricComparison() { return metricComparison; }
        public String getBestExperiment() { return bestExperiment; }
        public String getComparisonMetric() { return comparisonMetric; }
    }
    
    /**
     * Initialize experiment tracker
     */
    public MLOpsExperimentTracker(String dbPath, String artifactsPath) {
        this.dbPath = dbPath;
        this.artifactsPath = artifactsPath;
        this.executor = Executors.newFixedThreadPool(5);
        
        // Create artifacts directory
        try {
            Files.createDirectories(Paths.get(artifactsPath));
        } catch (IOException e) {
            logger.error("Failed to create artifacts directory", e);
        }
        
        // Initialize database
        initializeDatabase();
        
        logger.info("MLOps Experiment Tracker initialized with DB: {}, Artifacts: {}", dbPath, artifactsPath);
    }
    
    /**
     * Initialize SQLite database for experiments
     */
    private void initializeDatabase() {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            // Create experiments table
            conn.createStatement().execute(
                "CREATE TABLE IF NOT EXISTS experiments (" +
                "experiment_id TEXT PRIMARY KEY, " +
                "experiment_name TEXT NOT NULL, " +
                "description TEXT, " +
                "user_id TEXT NOT NULL, " +
                "project_name TEXT NOT NULL, " +
                "status TEXT NOT NULL, " +
                "start_time TEXT NOT NULL, " +
                "end_time TEXT, " +
                "parameters TEXT, " +
                "metrics TEXT, " +
                "tags TEXT, " +
                "artifacts TEXT, " +
                "hardware_info TEXT, " +
                "git_commit TEXT, " +
                "dependencies TEXT, " +
                "dataset_info TEXT" +
                ")"
            );
            
            // Create checkpoints table
            conn.createStatement().execute(
                "CREATE TABLE IF NOT EXISTS model_checkpoints (" +
                "checkpoint_id TEXT PRIMARY KEY, " +
                "experiment_id TEXT NOT NULL, " +
                "epoch INTEGER, " +
                "step INTEGER, " +
                "metrics TEXT, " +
                "model_path TEXT, " +
                "timestamp TEXT, " +
                "is_best INTEGER, " +
                "FOREIGN KEY (experiment_id) REFERENCES experiments (experiment_id)" +
                ")"
            );
            
            // Create indexes
            conn.createStatement().execute(
                "CREATE INDEX IF NOT EXISTS idx_experiments_project ON experiments (project_name)"
            );
            conn.createStatement().execute(
                "CREATE INDEX IF NOT EXISTS idx_experiments_user ON experiments (user_id)"
            );
            conn.createStatement().execute(
                "CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments (status)"
            );
            
            logger.info("Database initialized successfully");
            
        } catch (SQLException e) {
            logger.error("Failed to initialize database", e);
            throw new RuntimeException("Database initialization failed", e);
        }
    }
    
    /**
     * Start new experiment
     * Mumbai me nayi experiment ki shururat!
     */
    public String startExperiment(String experimentName, String userId, String projectName, String description) {
        String experimentId = generateExperimentId();
        
        ExperimentRun experiment = new ExperimentRun(experimentId, experimentName, userId, projectName);
        experiment.setDescription(description);
        experiment.setHardwareInfo(new HardwareInfo());
        
        // Simulate git commit detection
        experiment.setGitCommit(generateGitCommit());
        
        // Store in memory for active tracking
        activeExperiments.put(experimentId, experiment);
        
        // Store in database
        saveExperiment(experiment);
        
        logger.info("Started experiment: {} ({})", experimentName, experimentId);
        return experimentId;
    }
    
    /**
     * Log experiment parameter
     */
    public void logParameter(String experimentId, String paramName, Object paramValue) {
        ExperimentRun experiment = activeExperiments.get(experimentId);
        if (experiment != null) {
            experiment.getParameters().put(paramName, paramValue);
            
            // Update database asynchronously
            CompletableFuture.runAsync(() -> updateExperimentParameters(experimentId, experiment.getParameters()), executor);
            
            logger.debug("Logged parameter: {} = {} for experiment {}", paramName, paramValue, experimentId);
        } else {
            logger.warn("Experiment not found: {}", experimentId);
        }
    }
    
    /**
     * Log experiment metric
     */
    public void logMetric(String experimentId, String metricName, Object metricValue, long step) {
        ExperimentRun experiment = activeExperiments.get(experimentId);
        if (experiment != null) {
            // Store metric with step information
            String metricKey = metricName + "_step_" + step;
            experiment.getMetrics().put(metricKey, metricValue);
            
            // Also store latest value
            experiment.getMetrics().put(metricName, metricValue);
            
            // Update database asynchronously
            CompletableFuture.runAsync(() -> updateExperimentMetrics(experimentId, experiment.getMetrics()), executor);
            
            logger.debug("Logged metric: {} = {} (step {}) for experiment {}", metricName, metricValue, step, experimentId);
        } else {
            logger.warn("Experiment not found: {}", experimentId);
        }
    }
    
    /**
     * Log experiment artifact
     */
    public void logArtifact(String experimentId, String artifactName, String artifactPath) {
        ExperimentRun experiment = activeExperiments.get(experimentId);
        if (experiment != null) {
            // Copy artifact to experiment artifacts directory
            String experimentArtifactsDir = artifactsPath + "/" + experimentId;
            
            try {
                Files.createDirectories(Paths.get(experimentArtifactsDir));
                
                Path sourcePath = Paths.get(artifactPath);
                Path targetPath = Paths.get(experimentArtifactsDir, artifactName);
                
                if (Files.exists(sourcePath)) {
                    Files.copy(sourcePath, targetPath, StandardCopyOption.REPLACE_EXISTING);
                    experiment.getArtifacts().put(artifactName, targetPath.toString());
                    
                    // Update database asynchronously
                    CompletableFuture.runAsync(() -> updateExperimentArtifacts(experimentId, experiment.getArtifacts()), executor);
                    
                    logger.info("Logged artifact: {} for experiment {}", artifactName, experimentId);
                } else {
                    logger.warn("Artifact file not found: {}", artifactPath);
                }
                
            } catch (IOException e) {
                logger.error("Failed to copy artifact: " + artifactName, e);
            }
        } else {
            logger.warn("Experiment not found: {}", experimentId);
        }
    }
    
    /**
     * Log model checkpoint
     */
    public void logModelCheckpoint(String experimentId, int epoch, long step, Map<String, Double> metrics, String modelPath) {
        ExperimentRun experiment = activeExperiments.get(experimentId);
        if (experiment != null) {
            String checkpointId = experimentId + "_checkpoint_" + epoch + "_" + step;
            
            ModelCheckpoint checkpoint = new ModelCheckpoint(checkpointId, epoch, step, metrics, modelPath);
            
            // Determine if this is the best checkpoint (based on validation accuracy or primary metric)
            if (isBestCheckpoint(experiment, metrics)) {
                checkpoint.setBest(true);
                
                // Mark previous best as false
                experiment.getModelCheckpoints().forEach(cp -> cp.setBest(false));
            }
            
            experiment.getModelCheckpoints().add(checkpoint);
            
            // Save checkpoint to database
            saveModelCheckpoint(experimentId, checkpoint);
            
            logger.info("Logged model checkpoint: epoch {}, step {} for experiment {}", epoch, step, experimentId);
        } else {
            logger.warn("Experiment not found: {}", experimentId);
        }
    }
    
    /**
     * Add tag to experiment
     */
    public void addTag(String experimentId, String tag) {
        ExperimentRun experiment = activeExperiments.get(experimentId);
        if (experiment != null) {
            experiment.getTags().add(tag);
            
            // Update database asynchronously
            CompletableFuture.runAsync(() -> updateExperimentTags(experimentId, experiment.getTags()), executor);
            
            logger.debug("Added tag: {} to experiment {}", tag, experimentId);
        }
    }
    
    /**
     * Set dataset information
     */
    public void setDatasetInfo(String experimentId, DatasetInfo datasetInfo) {
        ExperimentRun experiment = activeExperiments.get(experimentId);
        if (experiment != null) {
            experiment.setDatasetInfo(datasetInfo);
            
            // Update database asynchronously
            CompletableFuture.runAsync(() -> updateExperimentDatasetInfo(experimentId, datasetInfo), executor);
            
            logger.info("Set dataset info for experiment {}: {} samples, {} features", 
                       experimentId, datasetInfo.getNumSamples(), datasetInfo.getNumFeatures());
        }
    }
    
    /**
     * End experiment
     */
    public void endExperiment(String experimentId, ExperimentStatus status) {
        ExperimentRun experiment = activeExperiments.get(experimentId);
        if (experiment != null) {
            experiment.setStatus(status);
            experiment.setEndTime(LocalDateTime.now());
            
            // Final save to database
            saveExperiment(experiment);
            
            // Remove from active experiments
            activeExperiments.remove(experimentId);
            
            logger.info("Ended experiment: {} with status {}", experimentId, status);
        }
    }
    
    /**
     * Get experiment by ID
     */
    public ExperimentRun getExperiment(String experimentId) {
        // Check active experiments first
        ExperimentRun experiment = activeExperiments.get(experimentId);
        if (experiment != null) {
            return experiment;
        }
        
        // Load from database
        return loadExperimentFromDatabase(experimentId);
    }
    
    /**
     * Search experiments with filters
     */
    public List<ExperimentRun> searchExperiments(String projectName, String userId, ExperimentStatus status, 
                                                Set<String> tags, int limit) {
        List<ExperimentRun> experiments = new ArrayList<>();
        
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            StringBuilder query = new StringBuilder("SELECT * FROM experiments WHERE 1=1");
            List<Object> params = new ArrayList<>();
            
            if (projectName != null) {
                query.append(" AND project_name = ?");
                params.add(projectName);
            }
            
            if (userId != null) {
                query.append(" AND user_id = ?");
                params.add(userId);
            }
            
            if (status != null) {
                query.append(" AND status = ?");
                params.add(status.name());
            }
            
            query.append(" ORDER BY start_time DESC LIMIT ?");
            params.add(limit);
            
            PreparedStatement stmt = conn.prepareStatement(query.toString());
            for (int i = 0; i < params.size(); i++) {
                stmt.setObject(i + 1, params.get(i));
            }
            
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                ExperimentRun experiment = resultSetToExperiment(rs);
                
                // Filter by tags if specified
                if (tags == null || tags.isEmpty() || 
                    experiment.getTags().stream().anyMatch(tags::contains)) {
                    experiments.add(experiment);
                }
            }
            
        } catch (SQLException e) {
            logger.error("Failed to search experiments", e);
        }
        
        return experiments;
    }
    
    /**
     * Compare experiments
     */
    public ExperimentComparison compareExperiments(List<String> experimentIds, String comparisonMetric) {
        ExperimentComparison comparison = new ExperimentComparison();
        comparison.setComparisonMetric(comparisonMetric);
        
        // Load experiments
        for (String experimentId : experimentIds) {
            ExperimentRun experiment = getExperiment(experimentId);
            if (experiment != null) {
                comparison.getExperiments().add(experiment);
            }
        }
        
        if (comparison.getExperiments().size() < 2) {
            logger.warn("Need at least 2 experiments for comparison");
            return comparison;
        }
        
        // Find common and different parameters
        analyzeParameters(comparison);
        
        // Compare metrics
        analyzeMetrics(comparison, comparisonMetric);
        
        return comparison;
    }
    
    /**
     * Generate experiment ID
     */
    private String generateExperimentId() {
        long counter = experimentCounter.incrementAndGet();
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        return "exp_" + timestamp + "_" + String.format("%04d", counter);
    }
    
    /**
     * Generate mock git commit
     */
    private String generateGitCommit() {
        return "commit_" + UUID.randomUUID().toString().substring(0, 8);
    }
    
    /**
     * Check if checkpoint is the best
     */
    private boolean isBestCheckpoint(ExperimentRun experiment, Map<String, Double> metrics) {
        // Simple heuristic: check if validation accuracy is the highest
        Double validationAcc = metrics.get("val_accuracy");
        if (validationAcc == null) {
            validationAcc = metrics.get("accuracy");
        }
        
        if (validationAcc != null) {
            return experiment.getModelCheckpoints().stream()
                    .mapToDouble(cp -> cp.getMetrics().getOrDefault("val_accuracy", 0.0))
                    .max().orElse(0.0) <= validationAcc;
        }
        
        return false;
    }
    
    /**
     * Database operations
     */
    private void saveExperiment(ExperimentRun experiment) {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "INSERT OR REPLACE INTO experiments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
            PreparedStatement stmt = conn.prepareStatement(sql);
            
            stmt.setString(1, experiment.getExperimentId());
            stmt.setString(2, experiment.getExperimentName());
            stmt.setString(3, experiment.getDescription());
            stmt.setString(4, experiment.getUserId());
            stmt.setString(5, experiment.getProjectName());
            stmt.setString(6, experiment.getStatus().name());
            stmt.setString(7, experiment.getStartTime().format(TIMESTAMP_FORMAT));
            stmt.setString(8, experiment.getEndTime() != null ? experiment.getEndTime().format(TIMESTAMP_FORMAT) : null);
            stmt.setString(9, objectMapper.writeValueAsString(experiment.getParameters()));
            stmt.setString(10, objectMapper.writeValueAsString(experiment.getMetrics()));
            stmt.setString(11, objectMapper.writeValueAsString(experiment.getTags()));
            stmt.setString(12, objectMapper.writeValueAsString(experiment.getArtifacts()));
            stmt.setString(13, objectMapper.writeValueAsString(experiment.getHardwareInfo()));
            stmt.setString(14, experiment.getGitCommit());
            stmt.setString(15, objectMapper.writeValueAsString(experiment.getDependencies()));
            stmt.setString(16, experiment.getDatasetInfo() != null ? 
                          objectMapper.writeValueAsString(experiment.getDatasetInfo()) : null);
            
            stmt.executeUpdate();
            
        } catch (Exception e) {
            logger.error("Failed to save experiment: " + experiment.getExperimentId(), e);
        }
    }
    
    private void saveModelCheckpoint(String experimentId, ModelCheckpoint checkpoint) {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "INSERT INTO model_checkpoints VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
            PreparedStatement stmt = conn.prepareStatement(sql);
            
            stmt.setString(1, checkpoint.getCheckpointId());
            stmt.setString(2, experimentId);
            stmt.setInt(3, checkpoint.getEpoch());
            stmt.setLong(4, checkpoint.getStep());
            stmt.setString(5, objectMapper.writeValueAsString(checkpoint.getMetrics()));
            stmt.setString(6, checkpoint.getModelPath());
            stmt.setString(7, checkpoint.getTimestamp().format(TIMESTAMP_FORMAT));
            stmt.setInt(8, checkpoint.isBest() ? 1 : 0);
            
            stmt.executeUpdate();
            
        } catch (Exception e) {
            logger.error("Failed to save checkpoint: " + checkpoint.getCheckpointId(), e);
        }
    }
    
    private void updateExperimentParameters(String experimentId, Map<String, Object> parameters) {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "UPDATE experiments SET parameters = ? WHERE experiment_id = ?";
            PreparedStatement stmt = conn.prepareStatement(sql);
            stmt.setString(1, objectMapper.writeValueAsString(parameters));
            stmt.setString(2, experimentId);
            stmt.executeUpdate();
        } catch (Exception e) {
            logger.error("Failed to update parameters for experiment: " + experimentId, e);
        }
    }
    
    private void updateExperimentMetrics(String experimentId, Map<String, Object> metrics) {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "UPDATE experiments SET metrics = ? WHERE experiment_id = ?";
            PreparedStatement stmt = conn.prepareStatement(sql);
            stmt.setString(1, objectMapper.writeValueAsString(metrics));
            stmt.setString(2, experimentId);
            stmt.executeUpdate();
        } catch (Exception e) {
            logger.error("Failed to update metrics for experiment: " + experimentId, e);
        }
    }
    
    private void updateExperimentArtifacts(String experimentId, Map<String, String> artifacts) {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "UPDATE experiments SET artifacts = ? WHERE experiment_id = ?";
            PreparedStatement stmt = conn.prepareStatement(sql);
            stmt.setString(1, objectMapper.writeValueAsString(artifacts));
            stmt.setString(2, experimentId);
            stmt.executeUpdate();
        } catch (Exception e) {
            logger.error("Failed to update artifacts for experiment: " + experimentId, e);
        }
    }
    
    private void updateExperimentTags(String experimentId, Set<String> tags) {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "UPDATE experiments SET tags = ? WHERE experiment_id = ?";
            PreparedStatement stmt = conn.prepareStatement(sql);
            stmt.setString(1, objectMapper.writeValueAsString(tags));
            stmt.setString(2, experimentId);
            stmt.executeUpdate();
        } catch (Exception e) {
            logger.error("Failed to update tags for experiment: " + experimentId, e);
        }
    }
    
    private void updateExperimentDatasetInfo(String experimentId, DatasetInfo datasetInfo) {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "UPDATE experiments SET dataset_info = ? WHERE experiment_id = ?";
            PreparedStatement stmt = conn.prepareStatement(sql);
            stmt.setString(1, objectMapper.writeValueAsString(datasetInfo));
            stmt.setString(2, experimentId);
            stmt.executeUpdate();
        } catch (Exception e) {
            logger.error("Failed to update dataset info for experiment: " + experimentId, e);
        }
    }
    
    private ExperimentRun loadExperimentFromDatabase(String experimentId) {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "SELECT * FROM experiments WHERE experiment_id = ?";
            PreparedStatement stmt = conn.prepareStatement(sql);
            stmt.setString(1, experimentId);
            
            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                return resultSetToExperiment(rs);
            }
            
        } catch (SQLException e) {
            logger.error("Failed to load experiment: " + experimentId, e);
        }
        
        return null;
    }
    
    private ExperimentRun resultSetToExperiment(ResultSet rs) throws SQLException {
        try {
            ExperimentRun experiment = new ExperimentRun();
            experiment.setExperimentId(rs.getString("experiment_id"));
            experiment.setExperimentName(rs.getString("experiment_name"));
            experiment.setDescription(rs.getString("description"));
            experiment.setUserId(rs.getString("user_id"));
            experiment.setProjectName(rs.getString("project_name"));
            experiment.setStatus(ExperimentStatus.valueOf(rs.getString("status")));
            experiment.setStartTime(LocalDateTime.parse(rs.getString("start_time"), TIMESTAMP_FORMAT));
            
            String endTimeStr = rs.getString("end_time");
            if (endTimeStr != null) {
                experiment.setEndTime(LocalDateTime.parse(endTimeStr, TIMESTAMP_FORMAT));
            }
            
            // Parse JSON fields
            String parametersJson = rs.getString("parameters");
            if (parametersJson != null) {
                experiment.setParameters(objectMapper.readValue(parametersJson, new TypeReference<Map<String, Object>>() {}));
            }
            
            String metricsJson = rs.getString("metrics");
            if (metricsJson != null) {
                experiment.setMetrics(objectMapper.readValue(metricsJson, new TypeReference<Map<String, Object>>() {}));
            }
            
            String tagsJson = rs.getString("tags");
            if (tagsJson != null) {
                experiment.setTags(objectMapper.readValue(tagsJson, new TypeReference<Set<String>>() {}));
            }
            
            return experiment;
            
        } catch (Exception e) {
            logger.error("Failed to parse experiment from ResultSet", e);
            throw new SQLException("Failed to parse experiment", e);
        }
    }
    
    private void analyzeParameters(ExperimentComparison comparison) {
        if (comparison.getExperiments().isEmpty()) return;
        
        // Find common parameters
        Map<String, Object> firstParams = comparison.getExperiments().get(0).getParameters();
        Map<String, Object> commonParams = new HashMap<>(firstParams);
        
        for (int i = 1; i < comparison.getExperiments().size(); i++) {
            Map<String, Object> params = comparison.getExperiments().get(i).getParameters();
            commonParams.entrySet().removeIf(entry -> !Objects.equals(entry.getValue(), params.get(entry.getKey())));
        }
        
        comparison.setCommonParameters(commonParams);
        
        // Find different parameters
        for (ExperimentRun experiment : comparison.getExperiments()) {
            Map<String, Object> differentParams = new HashMap<>(experiment.getParameters());
            differentParams.entrySet().removeIf(entry -> commonParams.containsKey(entry.getKey()));
            comparison.getDifferentParameters().put(experiment.getExperimentId(), differentParams);
        }
    }
    
    private void analyzeMetrics(ExperimentComparison comparison, String comparisonMetric) {
        String bestExperimentId = null;
        double bestMetricValue = Double.NEGATIVE_INFINITY;
        
        for (ExperimentRun experiment : comparison.getExperiments()) {
            Map<String, Object> metricComparison = new HashMap<>();
            
            for (Map.Entry<String, Object> entry : experiment.getMetrics().entrySet()) {
                metricComparison.put(entry.getKey(), entry.getValue());
            }
            
            comparison.getMetricComparison().put(experiment.getExperimentId(), metricComparison);
            
            // Find best experiment based on comparison metric
            if (comparisonMetric != null && experiment.getMetrics().containsKey(comparisonMetric)) {
                Object metricObj = experiment.getMetrics().get(comparisonMetric);
                if (metricObj instanceof Number) {
                    double metricValue = ((Number) metricObj).doubleValue();
                    if (metricValue > bestMetricValue) {
                        bestMetricValue = metricValue;
                        bestExperimentId = experiment.getExperimentId();
                    }
                }
            }
        }
        
        comparison.setBestExperiment(bestExperimentId);
    }
    
    /**
     * Shutdown the tracker
     */
    public void shutdown() {
        logger.info("Shutting down MLOps Experiment Tracker...");
        
        // Save all active experiments
        for (ExperimentRun experiment : activeExperiments.values()) {
            experiment.setStatus(ExperimentStatus.CANCELLED);
            experiment.setEndTime(LocalDateTime.now());
            saveExperiment(experiment);
        }
        
        executor.shutdown();
        try {
            if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        logger.info("MLOps Experiment Tracker shutdown complete");
    }
    
    /**
     * Demo main method
     */
    public static void main(String[] args) throws Exception {
        System.out.println("🧪 Starting MLOps Experiment Tracker Demo");
        System.out.println("=" + "=".repeat(50));
        
        // Initialize tracker
        MLOpsExperimentTracker tracker = new MLOpsExperimentTracker(
            "experiments.db", 
            "experiment_artifacts"
        );
        
        // Start experiments
        System.out.println("\n🚀 Starting sample experiments...");
        
        // Experiment 1: Fraud Detection Model
        String exp1 = tracker.startExperiment(
            "Paytm Fraud Detection v2",
            "data_scientist_1",
            "fraud_detection",
            "Improved fraud detection with feature engineering"
        );
        
        // Log parameters
        tracker.logParameter(exp1, "model_type", "random_forest");
        tracker.logParameter(exp1, "n_estimators", 100);
        tracker.logParameter(exp1, "max_depth", 10);
        tracker.logParameter(exp1, "learning_rate", 0.1);
        
        // Log dataset info
        tracker.setDatasetInfo(exp1, new DatasetInfo(
            "fraud_dataset_v2", "2.0", "/data/fraud_data.csv", 100000, 25
        ));
        
        // Add tags
        tracker.addTag(exp1, "fraud");
        tracker.addTag(exp1, "production");
        tracker.addTag(exp1, "random_forest");
        
        // Simulate training with metrics
        for (int epoch = 1; epoch <= 5; epoch++) {
            double accuracy = 0.8 + (epoch * 0.02) + Math.random() * 0.01;
            double precision = 0.75 + (epoch * 0.025) + Math.random() * 0.01;
            double recall = 0.7 + (epoch * 0.03) + Math.random() * 0.01;
            
            tracker.logMetric(exp1, "accuracy", accuracy, epoch);
            tracker.logMetric(exp1, "precision", precision, epoch);
            tracker.logMetric(exp1, "recall", recall, epoch);
            tracker.logMetric(exp1, "val_accuracy", accuracy - 0.02, epoch);
            
            // Log model checkpoint
            Map<String, Double> checkpointMetrics = Map.of(
                "accuracy", accuracy,
                "val_accuracy", accuracy - 0.02,
                "precision", precision,
                "recall", recall
            );
            
            tracker.logModelCheckpoint(exp1, epoch, epoch * 1000, checkpointMetrics, 
                                     "/models/fraud_model_epoch_" + epoch + ".pkl");
        }
        
        // Experiment 2: Recommendation System
        String exp2 = tracker.startExperiment(
            "Flipkart Recommendation v3",
            "ml_engineer_2", 
            "recommendation_system",
            "Deep learning based product recommendations"
        );
        
        tracker.logParameter(exp2, "model_type", "neural_network");
        tracker.logParameter(exp2, "embedding_dim", 128);
        tracker.logParameter(exp2, "hidden_layers", Arrays.asList(256, 128, 64));
        tracker.logParameter(exp2, "dropout_rate", 0.2);
        tracker.logParameter(exp2, "learning_rate", 0.001);
        
        tracker.setDatasetInfo(exp2, new DatasetInfo(
            "recommendation_dataset", "1.5", "/data/user_item_interactions.csv", 1000000, 50
        ));
        
        tracker.addTag(exp2, "recommendation");
        tracker.addTag(exp2, "deep_learning");
        tracker.addTag(exp2, "tensorflow");
        
        // Simulate training
        for (int epoch = 1; epoch <= 10; epoch++) {
            double loss = 2.0 - (epoch * 0.15) + Math.random() * 0.1;
            double accuracy = 0.6 + (epoch * 0.03) + Math.random() * 0.02;
            double precision_at_k = 0.4 + (epoch * 0.04) + Math.random() * 0.01;
            
            tracker.logMetric(exp2, "loss", loss, epoch);
            tracker.logMetric(exp2, "accuracy", accuracy, epoch);
            tracker.logMetric(exp2, "precision_at_k", precision_at_k, epoch);
            tracker.logMetric(exp2, "val_loss", loss + 0.1, epoch);
            tracker.logMetric(exp2, "val_accuracy", accuracy - 0.05, epoch);
            
            Map<String, Double> checkpointMetrics = Map.of(
                "loss", loss,
                "accuracy", accuracy,
                "val_accuracy", accuracy - 0.05,
                "precision_at_k", precision_at_k
            );
            
            tracker.logModelCheckpoint(exp2, epoch, epoch * 500, checkpointMetrics,
                                     "/models/recommendation_model_epoch_" + epoch + ".h5");
        }
        
        // End experiments
        tracker.endExperiment(exp1, ExperimentStatus.COMPLETED);
        tracker.endExperiment(exp2, ExperimentStatus.COMPLETED);
        
        // Wait for async operations
        Thread.sleep(1000);
        
        // Search experiments
        System.out.println("\n🔍 Searching experiments...");
        
        List<ExperimentRun> projectExperiments = tracker.searchExperiments(
            "fraud_detection", null, ExperimentStatus.COMPLETED, null, 10
        );
        System.out.println("Found " + projectExperiments.size() + " completed fraud detection experiments");
        
        List<ExperimentRun> allExperiments = tracker.searchExperiments(
            null, null, null, null, 10
        );
        System.out.println("Found " + allExperiments.size() + " total experiments");
        
        // Compare experiments
        System.out.println("\n⚖️  Comparing experiments...");
        
        ExperimentComparison comparison = tracker.compareExperiments(
            Arrays.asList(exp1, exp2), "accuracy"
        );
        
        System.out.println("Comparison Results:");
        System.out.println("  Experiments compared: " + comparison.getExperiments().size());
        System.out.println("  Best experiment (by accuracy): " + comparison.getBestExperiment());
        System.out.println("  Common parameters: " + comparison.getCommonParameters().size());
        
        // Display experiment details
        System.out.println("\n📊 Experiment Details:");
        
        for (ExperimentRun experiment : Arrays.asList(
            tracker.getExperiment(exp1), 
            tracker.getExperiment(exp2)
        )) {
            System.out.println("\n  " + experiment.getExperimentName() + " (" + experiment.getExperimentId() + "):");
            System.out.println("    Status: " + experiment.getStatus());
            System.out.println("    Parameters: " + experiment.getParameters().size());
            System.out.println("    Metrics: " + experiment.getMetrics().size());
            System.out.println("    Checkpoints: " + experiment.getModelCheckpoints().size());
            System.out.println("    Tags: " + experiment.getTags());
            
            // Show final metrics
            Object finalAccuracy = experiment.getMetrics().get("accuracy");
            if (finalAccuracy != null) {
                System.out.println("    Final Accuracy: " + String.format("%.4f", ((Number) finalAccuracy).doubleValue()));
            }
            
            // Show best checkpoint
            Optional<ModelCheckpoint> bestCheckpoint = experiment.getModelCheckpoints().stream()
                .filter(ModelCheckpoint::isBest)
                .findFirst();
            
            if (bestCheckpoint.isPresent()) {
                System.out.println("    Best Checkpoint: Epoch " + bestCheckpoint.get().getEpoch());
            }
        }
        
        System.out.println("\n✅ MLOps Experiment Tracker demo completed!");
        System.out.println("Mumbai me experiment tracking bhi scientific method ki tarah systematic!");
        
        // Shutdown
        tracker.shutdown();
    }
}
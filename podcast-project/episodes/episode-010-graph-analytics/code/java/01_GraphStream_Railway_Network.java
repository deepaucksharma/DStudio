/*
GraphStream Railway Network Analysis for Indian Railways
Production-grade graph analytics with real-time visualization

Author: Episode 10 - Graph Analytics at Scale  
Context: Indian Railways network analysis - stations, routes, aur passenger flow
*/

package com.indianrailways.graph;

import org.graphstream.graph.*;
import org.graphstream.graph.implementations.*;
import org.graphstream.algorithm.shortestpath.*;
import org.graphstream.algorithm.coloring.*;
import org.graphstream.algorithm.measure.*;
import org.graphstream.ui.view.Viewer;
import org.graphstream.ui.swing_viewer.SwingViewer;
import org.graphstream.ui.swing_viewer.ViewPanel;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.*;
import java.util.List;
import java.util.concurrent.*;
import java.util.stream.Collectors;

// Data models for Railway Network
class Station {
    private String stationCode;
    private String stationName;
    private String city;
    private String state;
    private String zone; // Railway zone
    private double latitude;
    private double longitude;
    private int platformCount;
    private long dailyPassengers;
    private boolean isMajorJunction;
    private StationType stationType;
    
    public enum StationType {
        TERMINUS, JUNCTION, HALT, CROSSING
    }
    
    // Constructor
    public Station(String stationCode, String stationName, String city, String state, String zone,
                  double latitude, double longitude, int platformCount, long dailyPassengers, 
                  boolean isMajorJunction, StationType stationType) {
        this.stationCode = stationCode;
        this.stationName = stationName;
        this.city = city;
        this.state = state;
        this.zone = zone;
        this.latitude = latitude;
        this.longitude = longitude;
        this.platformCount = platformCount;
        this.dailyPassengers = dailyPassengers;
        this.isMajorJunction = isMajorJunction;
        this.stationType = stationType;
    }
    
    // Getters
    public String getStationCode() { return stationCode; }
    public String getStationName() { return stationName; }
    public String getCity() { return city; }
    public String getState() { return state; }
    public String getZone() { return zone; }
    public double getLatitude() { return latitude; }
    public double getLongitude() { return longitude; }
    public int getPlatformCount() { return platformCount; }
    public long getDailyPassengers() { return dailyPassengers; }
    public boolean isMajorJunction() { return isMajorJunction; }
    public StationType getStationType() { return stationType; }
    
    @Override
    public String toString() {
        return String.format("%s (%s) - %s, %s", stationName, stationCode, city, state);
    }
}

class TrainRoute {
    private String routeId;
    private String fromStationCode;
    private String toStationCode;
    private double distance; // in kilometers
    private int travelTime; // in minutes
    private String trackType; // BROAD_GAUGE, METER_GAUGE, NARROW_GAUGE
    private boolean isElectrified;
    private int maxSpeed; // in km/h
    private int dailyTrains;
    private RouteType routeType;
    
    public enum RouteType {
        MAIN_LINE, BRANCH_LINE, LOOP_LINE, YARD_LINE
    }
    
    // Constructor
    public TrainRoute(String routeId, String fromStationCode, String toStationCode, 
                     double distance, int travelTime, String trackType, boolean isElectrified,
                     int maxSpeed, int dailyTrains, RouteType routeType) {
        this.routeId = routeId;
        this.fromStationCode = fromStationCode;
        this.toStationCode = toStationCode;
        this.distance = distance;
        this.travelTime = travelTime;
        this.trackType = trackType;
        this.isElectrified = isElectrified;
        this.maxSpeed = maxSpeed;
        this.dailyTrains = dailyTrains;
        this.routeType = routeType;
    }
    
    // Getters
    public String getRouteId() { return routeId; }
    public String getFromStationCode() { return fromStationCode; }
    public String getToStationCode() { return toStationCode; }
    public double getDistance() { return distance; }
    public int getTravelTime() { return travelTime; }
    public String getTrackType() { return trackType; }
    public boolean isElectrified() { return isElectrified; }
    public int getMaxSpeed() { return maxSpeed; }
    public int getDailyTrains() { return dailyTrains; }
    public RouteType getRouteType() { return routeType; }
}

// Main Railway Network Analysis Service
public class IndianRailwayGraphAnalyzer {
    
    private Graph railwayGraph;
    private Map<String, Station> stations;
    private Map<String, TrainRoute> routes;
    private DijkstraShortestPath shortestPathAlgorithm;
    private Betweenness betweennessAlgorithm;
    private GreedyColoring coloringAlgorithm;
    
    // Performance metrics
    private long totalAnalysisTime;
    private int totalQueries;
    private Map<String, Long> algorithmPerformance;
    
    // UI components
    private JFrame mainFrame;
    private ViewPanel viewPanel;
    private JPanel controlPanel;
    
    public IndianRailwayGraphAnalyzer() {
        System.out.println("🚂 Indian Railway Network - GraphStream Analytics");
        System.out.println("=".repeat(60));
        
        // Initialize graph with enhanced styling
        railwayGraph = new MultiGraph("Indian Railway Network");
        stations = new HashMap<>();
        routes = new HashMap<>();
        algorithmPerformance = new HashMap<>();
        
        // Enable auto-layout and styling
        railwayGraph.addAttribute("ui.stylesheet", getGraphStylesheet());
        railwayGraph.addAttribute("ui.quality");
        railwayGraph.addAttribute("ui.antialias");
        
        // Initialize algorithms
        shortestPathAlgorithm = new DijkstraShortestPath(Dijkstra.Element.EDGE, null, "distance");
        betweennessAlgorithm = new Betweenness();
        coloringAlgorithm = new GreedyColoring("ui.color");
        
        // Initialize algorithms on graph
        shortestPathAlgorithm.init(railwayGraph);
        betweennessAlgorithm.init(railwayGraph);
        coloringAlgorithm.init(railwayGraph);
        
        System.out.println("✅ Railway Graph Analyzer initialized");
        
        // Load demo data
        loadDemoRailwayNetwork();
        
        // Setup UI
        setupUserInterface();
    }
    
    private void loadDemoRailwayNetwork() {
        System.out.println("\n🏗️  Loading Indian Railway Network Data...");
        
        // Major Indian Railway Stations (demo subset)
        Station[] demoStations = {
            // Northern Railway
            new Station("NDLS", "New Delhi", "New Delhi", "Delhi", "Northern", 
                       28.6414, 77.2085, 16, 500000, true, Station.StationType.TERMINUS),
            new Station("MB", "Mumbai Central", "Mumbai", "Maharashtra", "Western", 
                       19.0634, 72.8192, 9, 1200000, true, Station.StationType.TERMINUS),
            new Station("HWH", "Howrah Junction", "Howrah", "West Bengal", "Eastern", 
                       22.5833, 88.3467, 23, 1000000, true, Station.StationType.JUNCTION),
            new Station("MAS", "Chennai Central", "Chennai", "Tamil Nadu", "Southern", 
                       13.0827, 80.2707, 12, 800000, true, Station.StationType.TERMINUS),
            new Station("SBC", "KSR Bangalore", "Bangalore", "Karnataka", "South Western", 
                       12.9716, 77.5946, 10, 600000, true, Station.StationType.JUNCTION),
            
            // Important Junctions
            new Station("JUC", "Jalandhar City", "Jalandhar", "Punjab", "Northern", 
                       31.3260, 75.5762, 6, 150000, true, Station.StationType.JUNCTION),
            new Station("NGP", "Nagpur", "Nagpur", "Maharashtra", "South East Central", 
                       21.1458, 79.0882, 8, 300000, true, Station.StationType.JUNCTION),
            new Station("BZA", "Vijayawada Junction", "Vijayawada", "Andhra Pradesh", "South Central", 
                       16.5062, 80.6480, 10, 400000, true, Station.StationType.JUNCTION),
            new Station("JAT", "Jammu Tawi", "Jammu", "Jammu & Kashmir", "Northern", 
                       32.7266, 74.8570, 5, 100000, false, Station.StationType.TERMINUS),
            new Station("TVC", "Thiruvananthapuram Central", "Thiruvananthapuram", "Kerala", "Southern", 
                       8.5041, 76.9558, 5, 200000, false, Station.StationType.TERMINUS),
            
            // Metro Cities Additional
            new Station("PUNE", "Pune Junction", "Pune", "Maharashtra", "Central", 
                       18.5204, 73.8567, 6, 350000, true, Station.StationType.JUNCTION),
            new Station("HYB", "Hyderabad Deccan", "Hyderabad", "Telangana", "South Central", 
                       17.3850, 78.4867, 7, 450000, true, Station.StationType.JUNCTION),
            new Station("JP", "Jaipur", "Jaipur", "Rajasthan", "North Western", 
                       26.9124, 75.7873, 6, 250000, true, Station.StationType.JUNCTION),
            new Station("LKO", "Lucknow", "Lucknow", "Uttar Pradesh", "Northern", 
                       26.8467, 80.9462, 8, 300000, true, Station.StationType.JUNCTION),
            new Station("INDB", "Indore Junction", "Indore", "Madhya Pradesh", "Western", 
                       22.7196, 75.8577, 5, 200000, false, Station.StationType.JUNCTION)
        };
        
        // Add stations to graph and storage
        for (Station station : demoStations) {
            addStationToGraph(station);
        }
        
        // Major Railway Routes (demo subset)
        TrainRoute[] demoRoutes = {
            // Golden Quadrilateral routes
            new TrainRoute("R001", "NDLS", "MB", 1384, 960, "BROAD_GAUGE", true, 130, 15, TrainRoute.RouteType.MAIN_LINE),
            new TrainRoute("R002", "MB", "MAS", 1279, 840, "BROAD_GAUGE", true, 120, 12, TrainRoute.RouteType.MAIN_LINE),
            new TrainRoute("R003", "MAS", "HWH", 1663, 1080, "BROAD_GAUGE", true, 110, 10, TrainRoute.RouteType.MAIN_LINE),
            new TrainRoute("R004", "HWH", "NDLS", 1441, 900, "BROAD_GAUGE", true, 120, 18, TrainRoute.RouteType.MAIN_LINE),
            
            // Diagonal routes
            new TrainRoute("R005", "NDLS", "MAS", 2180, 1380, "BROAD_GAUGE", true, 110, 8, TrainRoute.RouteType.MAIN_LINE),
            new TrainRoute("R006", "MB", "HWH", 1968, 1260, "BROAD_GAUGE", true, 100, 6, TrainRoute.RouteType.MAIN_LINE),
            
            // Regional connections
            new TrainRoute("R007", "NDLS", "JUC", 356, 240, "BROAD_GAUGE", true, 110, 20, TrainRoute.RouteType.BRANCH_LINE),
            new TrainRoute("R008", "NGP", "BZA", 588, 420, "BROAD_GAUGE", true, 100, 8, TrainRoute.RouteType.MAIN_LINE),
            new TrainRoute("R009", "SBC", "MAS", 362, 300, "BROAD_GAUGE", true, 90, 25, TrainRoute.RouteType.MAIN_LINE),
            new TrainRoute("R010", "PUNE", "MB", 192, 180, "BROAD_GAUGE", true, 80, 30, TrainRoute.RouteType.MAIN_LINE),
            
            // Additional connections
            new TrainRoute("R011", "NDLS", "LKO", 495, 360, "BROAD_GAUGE", true, 110, 12, TrainRoute.RouteType.MAIN_LINE),
            new TrainRoute("R012", "JP", "NDLS", 308, 240, "BROAD_GAUGE", true, 100, 15, TrainRoute.RouteType.MAIN_LINE),
            new TrainRoute("R013", "HYB", "BZA", 275, 240, "BROAD_GAUGE", true, 85, 18, TrainRoute.RouteType.BRANCH_LINE),
            new TrainRoute("R014", "MAS", "TVC", 695, 540, "BROAD_GAUGE", true, 90, 10, TrainRoute.RouteType.MAIN_LINE),
            new TrainRoute("R015", "INDB", "MB", 588, 480, "BROAD_GAUGE", true, 95, 8, TrainRoute.RouteType.BRANCH_LINE)
        };
        
        // Add routes to graph and storage
        for (TrainRoute route : demoRoutes) {
            addRouteToGraph(route);
        }
        
        System.out.printf("✅ Loaded network: %d stations, %d routes\n", 
                         demoStations.length, demoRoutes.length);
        
        // Calculate initial metrics
        calculateNetworkMetrics();
    }
    
    private void addStationToGraph(Station station) {
        // Add node to graph
        Node node = railwayGraph.addNode(station.getStationCode());
        
        // Set node attributes
        node.addAttribute("ui.label", station.getStationName() + " (" + station.getStationCode() + ")");
        node.addAttribute("layout.weight", station.getDailyPassengers() / 100000.0); // Scale for layout
        node.addAttribute("station.name", station.getStationName());
        node.addAttribute("station.city", station.getCity());
        node.addAttribute("station.state", station.getState());
        node.addAttribute("station.zone", station.getZone());
        node.addAttribute("station.passengers", station.getDailyPassengers());
        node.addAttribute("station.platforms", station.getPlatformCount());
        node.addAttribute("station.type", station.getStationType().toString());
        node.addAttribute("station.major", station.isMajorJunction());
        
        // Visual styling based on station importance
        if (station.isMajorJunction()) {
            node.addAttribute("ui.class", "major-station");
        } else {
            node.addAttribute("ui.class", "regular-station");
        }
        
        // Size based on passenger volume
        double size = Math.max(10, Math.min(30, station.getDailyPassengers() / 50000.0));
        node.addAttribute("ui.size", size);
        
        // Store station
        stations.put(station.getStationCode(), station);
    }
    
    private void addRouteToGraph(TrainRoute route) {
        // Check if both stations exist
        if (!railwayGraph.getNode(route.getFromStationCode()) || 
            !railwayGraph.getNode(route.getToStationCode())) {
            System.err.printf("Warning: Route %s references non-existent station(s)\n", route.getRouteId());
            return;
        }
        
        // Add edge to graph
        Edge edge = railwayGraph.addEdge(route.getRouteId(), 
                                       route.getFromStationCode(), 
                                       route.getToStationCode(), 
                                       false); // undirected
        
        // Set edge attributes
        edge.addAttribute("distance", route.getDistance());
        edge.addAttribute("travel_time", route.getTravelTime());
        edge.addAttribute("track_type", route.getTrackType());
        edge.addAttribute("electrified", route.isElectrified());
        edge.addAttribute("max_speed", route.getMaxSpeed());
        edge.addAttribute("daily_trains", route.getDailyTrains());
        edge.addAttribute("route_type", route.getRouteType().toString());
        
        // Visual styling based on route importance
        if (route.getRouteType() == TrainRoute.RouteType.MAIN_LINE) {
            edge.addAttribute("ui.class", "main-line");
        } else {
            edge.addAttribute("ui.class", "branch-line");
        }
        
        // Edge thickness based on daily trains
        double thickness = Math.max(1, Math.min(5, route.getDailyTrains() / 5.0));
        edge.addAttribute("ui.size", thickness);
        
        // Edge label
        edge.addAttribute("ui.label", String.format("%.0f km", route.getDistance()));
        
        // Store route
        routes.put(route.getRouteId(), route);
    }
    
    private void calculateNetworkMetrics() {
        System.out.println("\n📊 Calculating Network Metrics...");
        
        long startTime = System.currentTimeMillis();
        
        // Basic graph metrics
        int nodeCount = railwayGraph.getNodeCount();
        int edgeCount = railwayGraph.getEdgeCount();
        double density = (2.0 * edgeCount) / (nodeCount * (nodeCount - 1));
        
        System.out.printf("   Network Size: %d stations, %d routes\n", nodeCount, edgeCount);
        System.out.printf("   Network Density: %.4f\n", density);
        
        // Calculate betweenness centrality
        betweennessAlgorithm.compute();
        
        // Find most central stations
        List<Node> nodesByBetweenness = new ArrayList<>();
        for (Node node : railwayGraph.getNodeSet()) {
            nodesByBetweenness.add(node);
        }
        nodesByBetweenness.sort((a, b) -> 
            Double.compare(b.getNumber("Cb"), a.getNumber("Cb")));
        
        System.out.println("\n🎯 Most Central Stations (Betweenness):");
        for (int i = 0; i < Math.min(5, nodesByBetweenness.size()); i++) {
            Node node = nodesByBetweenness.get(i);
            System.out.printf("   %d. %s - Centrality: %.6f\n", 
                i + 1, 
                node.getAttribute("station.name"), 
                node.getNumber("Cb"));
        }
        
        // Calculate degree distribution
        Map<Integer, Integer> degreeDistribution = new HashMap<>();
        for (Node node : railwayGraph.getNodeSet()) {
            int degree = node.getDegree();
            degreeDistribution.put(degree, degreeDistribution.getOrDefault(degree, 0) + 1);
        }
        
        System.out.println("\n📈 Degree Distribution:");
        degreeDistribution.entrySet().stream()
            .sorted(Map.Entry.<Integer, Integer>comparingByKey().reversed())
            .limit(5)
            .forEach(entry -> 
                System.out.printf("   Degree %d: %d stations\n", entry.getKey(), entry.getValue()));
        
        long endTime = System.currentTimeMillis();
        algorithmPerformance.put("NetworkMetrics", endTime - startTime);
        
        System.out.printf("⏱️  Metrics calculation completed in %d ms\n", endTime - startTime);
    }
    
    public List<String> findShortestPath(String fromStation, String toStation) {
        long startTime = System.currentTimeMillis();
        
        shortestPathAlgorithm.setSource(railwayGraph.getNode(fromStation));
        shortestPathAlgorithm.compute();
        
        Path path = shortestPathAlgorithm.getPath(railwayGraph.getNode(toStation));
        
        List<String> pathStations = new ArrayList<>();
        if (path != null) {
            for (Node node : path.getNodePath()) {
                pathStations.add(node.getId());
            }
        }
        
        long endTime = System.currentTimeMillis();
        algorithmPerformance.put("ShortestPath", endTime - startTime);
        totalQueries++;
        
        return pathStations;
    }
    
    public double calculatePathDistance(List<String> pathStations) {
        if (pathStations.size() < 2) return 0.0;
        
        double totalDistance = 0.0;
        for (int i = 0; i < pathStations.size() - 1; i++) {
            Edge edge = railwayGraph.getNode(pathStations.get(i))
                                  .getEdgeBetween(railwayGraph.getNode(pathStations.get(i + 1)));
            if (edge != null) {
                totalDistance += edge.getNumber("distance");
            }
        }
        return totalDistance;
    }
    
    public int calculatePathTime(List<String> pathStations) {
        if (pathStations.size() < 2) return 0;
        
        int totalTime = 0;
        for (int i = 0; i < pathStations.size() - 1; i++) {
            Edge edge = railwayGraph.getNode(pathStations.get(i))
                                  .getEdgeBetween(railwayGraph.getNode(pathStations.get(i + 1)));
            if (edge != null) {
                totalTime += edge.getNumber("travel_time");
            }
        }
        return totalTime;
    }
    
    public List<String> findAlternativePaths(String fromStation, String toStation, int maxPaths) {
        // Simplified alternative path finding
        // In production, use more sophisticated algorithms
        List<String> alternatives = new ArrayList<>();
        
        // Find paths through different major junctions
        String[] majorJunctions = {"NDLS", "MB", "HWH", "MAS", "NGP", "BZA"};
        
        for (String junction : majorJunctions) {
            if (!junction.equals(fromStation) && !junction.equals(toStation)) {
                List<String> path1 = findShortestPath(fromStation, junction);
                List<String> path2 = findShortestPath(junction, toStation);
                
                if (!path1.isEmpty() && !path2.isEmpty()) {
                    // Combine paths
                    List<String> fullPath = new ArrayList<>(path1);
                    fullPath.addAll(path2.subList(1, path2.size())); // Skip duplicate junction
                    
                    double distance = calculatePathDistance(fullPath);
                    alternatives.add(String.format("Via %s: %d stations, %.0f km", 
                                                  junction, fullPath.size(), distance));
                    
                    if (alternatives.size() >= maxPaths) break;
                }
            }
        }
        
        return alternatives;
    }
    
    private String getGraphStylesheet() {
        return """
            graph {
                fill-color: #f8f9fa;
                padding: 50px;
            }
            
            node {
                fill-color: #007bff;
                stroke-mode: plain;
                stroke-color: #0056b3;
                stroke-width: 2px;
                text-color: #000;
                text-size: 12px;
                text-alignment: above;
                shape: circle;
            }
            
            node.major-station {
                fill-color: #dc3545;
                stroke-color: #b21f2d;
                stroke-width: 3px;
                text-size: 14px;
                text-weight: bold;
            }
            
            edge {
                fill-color: #6c757d;
                stroke-mode: plain;
                stroke-width: 2px;
                text-color: #495057;
                text-size: 10px;
                arrow-size: 6px;
            }
            
            edge.main-line {
                fill-color: #28a745;
                stroke-color: #1e7e34;
                stroke-width: 3px;
            }
            
            edge.highlighted {
                fill-color: #ffc107;
                stroke-color: #d39e00;
                stroke-width: 4px;
            }
            
            node.highlighted {
                fill-color: #ffc107;
                stroke-color: #d39e00;
                stroke-width: 4px;
            }
        """;
    }
    
    private void setupUserInterface() {
        // Create main frame
        mainFrame = new JFrame("Indian Railway Network Analysis");
        mainFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        mainFrame.setLayout(new BorderLayout());
        
        // Create graph viewer
        Viewer viewer = railwayGraph.display(false);
        viewPanel = (ViewPanel) viewer.getDefaultView();
        viewPanel.setPreferredSize(new Dimension(800, 600));
        
        // Create control panel
        setupControlPanel();
        
        // Add components to frame
        mainFrame.add(viewPanel, BorderLayout.CENTER);
        mainFrame.add(controlPanel, BorderLayout.EAST);
        
        // Set frame properties
        mainFrame.setSize(1200, 800);
        mainFrame.setLocationRelativeTo(null);
        mainFrame.setVisible(true);
        
        System.out.println("🖥️  Interactive UI launched");
    }
    
    private void setupControlPanel() {
        controlPanel = new JPanel();
        controlPanel.setLayout(new BoxLayout(controlPanel, BoxLayout.Y_AXIS));
        controlPanel.setPreferredSize(new Dimension(300, 600));
        controlPanel.setBorder(BorderFactory.createTitledBorder("Railway Network Analysis"));
        
        // Station selection
        JLabel fromLabel = new JLabel("From Station:");
        JComboBox<String> fromCombo = new JComboBox<>(stations.keySet().toArray(new String[0]));
        
        JLabel toLabel = new JLabel("To Station:");
        JComboBox<String> toCombo = new JComboBox<>(stations.keySet().toArray(new String[0]));
        
        // Path finding button
        JButton findPathButton = new JButton("Find Shortest Path");
        findPathButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                String fromStation = (String) fromCombo.getSelectedItem();
                String toStation = (String) toCombo.getSelectedItem();
                
                if (fromStation != null && toStation != null && !fromStation.equals(toStation)) {
                    findAndHighlightPath(fromStation, toStation);
                }
            }
        });
        
        // Results area
        JLabel resultsLabel = new JLabel("Results:");
        JTextArea resultsArea = new JTextArea(15, 25);
        resultsArea.setEditable(false);
        resultsArea.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 11));
        JScrollPane scrollPane = new JScrollPane(resultsArea);
        
        // Analysis buttons
        JButton metricsButton = new JButton("Network Metrics");
        metricsButton.addActionListener(e -> displayNetworkMetrics(resultsArea));
        
        JButton centralityButton = new JButton("Station Centrality");
        centralityButton.addActionListener(e -> displayCentralityAnalysis(resultsArea));
        
        JButton clearButton = new JButton("Clear Highlights");
        clearButton.addActionListener(e -> clearHighlights());
        
        // Add components to control panel
        controlPanel.add(Box.createVerticalStrut(10));
        controlPanel.add(fromLabel);
        controlPanel.add(fromCombo);
        controlPanel.add(Box.createVerticalStrut(10));
        controlPanel.add(toLabel);
        controlPanel.add(toCombo);
        controlPanel.add(Box.createVerticalStrut(15));
        controlPanel.add(findPathButton);
        controlPanel.add(Box.createVerticalStrut(15));
        controlPanel.add(metricsButton);
        controlPanel.add(centralityButton);
        controlPanel.add(clearButton);
        controlPanel.add(Box.createVerticalStrut(15));
        controlPanel.add(resultsLabel);
        controlPanel.add(scrollPane);
        
        // Store reference for updates
        this.resultsArea = resultsArea;
    }
    
    private JTextArea resultsArea; // Instance variable for results display
    
    private void findAndHighlightPath(String fromStation, String toStation) {
        // Clear previous highlights
        clearHighlights();
        
        // Find shortest path
        List<String> path = findShortestPath(fromStation, toStation);
        
        if (path.isEmpty()) {
            resultsArea.setText("No path found between " + fromStation + " and " + toStation);
            return;
        }
        
        // Highlight path
        highlightPath(path);
        
        // Calculate metrics
        double distance = calculatePathDistance(path);
        int travelTime = calculatePathTime(path);
        
        // Display results
        StringBuilder results = new StringBuilder();
        results.append("🚂 SHORTEST PATH ANALYSIS\n");
        results.append("=".repeat(30)).append("\n\n");
        results.append("From: ").append(stations.get(fromStation).getStationName()).append("\n");
        results.append("To: ").append(stations.get(toStation).getStationName()).append("\n\n");
        results.append("Path Details:\n");
        
        for (int i = 0; i < path.size(); i++) {
            String stationCode = path.get(i);
            Station station = stations.get(stationCode);
            results.append(String.format("%2d. %s (%s)\n", i + 1, 
                                        station.getStationName(), stationCode));
        }
        
        results.append(String.format("\nTotal Distance: %.0f km\n", distance));
        results.append(String.format("Estimated Time: %d minutes (%.1f hours)\n", 
                                    travelTime, travelTime / 60.0));
        results.append(String.format("Stations: %d\n", path.size()));
        
        // Alternative paths
        List<String> alternatives = findAlternativePaths(fromStation, toStation, 3);
        if (!alternatives.isEmpty()) {
            results.append("\n🛤️  Alternative Routes:\n");
            for (String alt : alternatives) {
                results.append("• ").append(alt).append("\n");
            }
        }
        
        resultsArea.setText(results.toString());
    }
    
    private void highlightPath(List<String> path) {
        // Highlight nodes
        for (String stationCode : path) {
            Node node = railwayGraph.getNode(stationCode);
            if (node != null) {
                node.addAttribute("ui.class", "highlighted");
            }
        }
        
        // Highlight edges
        for (int i = 0; i < path.size() - 1; i++) {
            Edge edge = railwayGraph.getNode(path.get(i))
                                  .getEdgeBetween(railwayGraph.getNode(path.get(i + 1)));
            if (edge != null) {
                edge.addAttribute("ui.class", "highlighted");
            }
        }
    }
    
    private void clearHighlights() {
        // Clear node highlights
        for (Node node : railwayGraph.getNodeSet()) {
            Station station = stations.get(node.getId());
            if (station != null && station.isMajorJunction()) {
                node.addAttribute("ui.class", "major-station");
            } else {
                node.addAttribute("ui.class", "regular-station");
            }
        }
        
        // Clear edge highlights
        for (Edge edge : railwayGraph.getEdgeSet()) {
            TrainRoute route = routes.get(edge.getId());
            if (route != null && route.getRouteType() == TrainRoute.RouteType.MAIN_LINE) {
                edge.addAttribute("ui.class", "main-line");
            } else {
                edge.removeAttribute("ui.class");
            }
        }
    }
    
    private void displayNetworkMetrics(JTextArea area) {
        StringBuilder metrics = new StringBuilder();
        metrics.append("📊 NETWORK METRICS\n");
        metrics.append("=".repeat(25)).append("\n\n");
        
        int nodeCount = railwayGraph.getNodeCount();
        int edgeCount = railwayGraph.getEdgeCount();
        double density = (2.0 * edgeCount) / (nodeCount * (nodeCount - 1));
        
        metrics.append(String.format("Stations: %d\n", nodeCount));
        metrics.append(String.format("Routes: %d\n", edgeCount));
        metrics.append(String.format("Density: %.4f\n", density));
        
        // Calculate total network distance
        double totalDistance = 0;
        for (Edge edge : railwayGraph.getEdgeSet()) {
            totalDistance += edge.getNumber("distance");
        }
        metrics.append(String.format("Total Distance: %.0f km\n", totalDistance));
        
        // Zone distribution
        Map<String, Long> zoneCount = stations.values().stream()
            .collect(Collectors.groupingBy(Station::getZone, Collectors.counting()));
        
        metrics.append("\n🚉 Zone Distribution:\n");
        zoneCount.entrySet().stream()
            .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
            .forEach(entry -> 
                metrics.append(String.format("• %s: %d stations\n", entry.getKey(), entry.getValue())));
        
        // Performance metrics
        metrics.append("\n⚡ Performance:\n");
        algorithmPerformance.forEach((algorithm, time) ->
            metrics.append(String.format("• %s: %d ms\n", algorithm, time)));
        
        area.setText(metrics.toString());
    }
    
    private void displayCentralityAnalysis(JTextArea area) {
        StringBuilder analysis = new StringBuilder();
        analysis.append("🎯 CENTRALITY ANALYSIS\n");
        analysis.append("=".repeat(28)).append("\n\n");
        
        // Recalculate betweenness if needed
        betweennessAlgorithm.compute();
        
        // Sort stations by betweenness centrality
        List<Node> nodesByBetweenness = new ArrayList<>();
        for (Node node : railwayGraph.getNodeSet()) {
            nodesByBetweenness.add(node);
        }
        nodesByBetweenness.sort((a, b) -> 
            Double.compare(b.getNumber("Cb"), a.getNumber("Cb")));
        
        analysis.append("Most Central Stations:\n");
        for (int i = 0; i < Math.min(10, nodesByBetweenness.size()); i++) {
            Node node = nodesByBetweenness.get(i);
            Station station = stations.get(node.getId());
            analysis.append(String.format("%2d. %s\n", i + 1, station.getStationName()));
            analysis.append(String.format("    Centrality: %.6f\n", node.getNumber("Cb")));
            analysis.append(String.format("    Daily Passengers: %,d\n", station.getDailyPassengers()));
            analysis.append(String.format("    Connections: %d\n\n", node.getDegree()));
        }
        
        area.setText(analysis.toString());
    }
    
    public static void main(String[] args) {
        // Set system properties for better graphics
        System.setProperty("org.graphstream.ui.renderer", "org.graphstream.ui.j2dviewer.J2DGraphRenderer");
        
        // Create and start the analyzer
        SwingUtilities.invokeLater(() -> {
            try {
                new IndianRailwayGraphAnalyzer();
            } catch (Exception e) {
                e.printStackTrace();
                JOptionPane.showMessageDialog(null, 
                    "Failed to initialize Railway Network Analyzer: " + e.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
            }
        });
        
        System.out.println("\n" + "=".repeat(60));
        System.out.println("📚 LEARNING POINTS:");
        System.out.println("• GraphStream Java mein real-time graph visualization provide karta hai");
        System.out.println("• Railway networks natural graph structures hai - stations aur routes");
        System.out.println("• Shortest path algorithms route planning ke liye essential hai");
        System.out.println("• Centrality measures important stations identify karte hai");
        System.out.println("• Interactive visualization analysis ko easier banata hai");
        System.out.println("• Graph algorithms transportation optimization mein critical role play karte hai");
        System.out.println("• Real-time updates aur dynamic analysis possible hai GraphStream se");
    }
}
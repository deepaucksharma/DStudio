# Design Google Maps

## Problem Statement

"Design a mapping service like Google Maps that provides maps, directions, real-time traffic, and location search for billions of users worldwide."

## Clarifying Questions

1. **Core Features**
   - Map rendering and display?
   - Turn-by-turn navigation?
   - Real-time traffic?
   - Location search (POIs)?
   - Street View?
   - Offline maps?

2. **Scale Requirements**
   - Number of users? (1 billion+)
   - Requests per second? (1M+ QPS)
   - Map data size? (Petabytes)
   - Update frequency? (Real-time for traffic)

3. **Technical Requirements**
   - Supported platforms? (Web, iOS, Android)
   - Accuracy requirements? (Meters)
   - Latency targets? (<200ms for tiles)
   - Offline support needed?

4. **Data Sources**
   - Satellite imagery?
   - Street-level data?
   - User contributions?
   - Traffic sensors?

## Requirements Summary

### Functional Requirements
- Map rendering at multiple zoom levels
- Location search and geocoding
- Route calculation (driving, walking, transit)
- Real-time traffic updates
- Turn-by-turn navigation
- Points of Interest (POI) information

### Non-Functional Requirements
- **Scale**: 1B+ users, 1M+ QPS
- **Latency**: <200ms for map tiles, <1s for routing
- **Availability**: 99.9% uptime
- **Accuracy**: Within 5 meters for GPS
- **Global**: Coverage for 220+ countries

### Out of Scope
- Street View implementation
- Indoor mapping
- AR navigation
- Business listings management

## Scale Estimation

### Data Size
```
Map Data:
- Vector data: 100 TB (roads, boundaries, POIs)
- Satellite imagery: 10 PB (multiple zoom levels)
- Street view: 50 PB
- Traffic data: 1 TB/day

Total storage: ~70 PB with redundancy
```

### Request Volume
```
Daily active users: 500 million
Average session: 10 map views, 2 searches, 1 route
Daily requests:
- Map tiles: 5B requests
- Search: 1B requests  
- Routing: 500M requests
- Traffic updates: 10B requests

Peak QPS:
- Map tiles: 1M QPS
- Search: 100K QPS
- Routing: 50K QPS
```

### Compute Requirements
```
Map rendering: 10,000 servers
Routing engines: 5,000 servers
Search clusters: 3,000 servers
Traffic processing: 2,000 servers
```

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│            (Web, iOS, Android, Embedded)                     │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                          CDN                                 │
│              (Map Tiles, Static Assets)                      │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway                              │
│                  (Load Balancing)                            │
└─────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────┬───────┴────────┬─────────────┐
        ▼              ▼                ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Map Tile    │ │   Search     │ │   Routing    │ │   Traffic    │
│  Service     │ │   Service    │ │   Service    │ │   Service    │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │              │                │             │
        └──────────────┴────────────────┴─────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │  Spatial  │ │  Graph   │ │   POI    │ │  Traffic │      │
│  │    DB     │ │    DB    │ │    DB    │ │    DB    │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Component Design

### 1. Map Data Model

**Tile-Based System**
```
Zoom Level 0: 1 tile (whole world)
Zoom Level 1: 4 tiles (2x2)
Zoom Level 2: 16 tiles (4x4)
...
Zoom Level 20: 1 trillion tiles

Tile Addressing:
/tiles/{z}/{x}/{y}.png
where z = zoom level, x = column, y = row
```

**Quadtree Structure**
```python
class QuadTree:
    def __init__(self, bounds):
        self.bounds = bounds
        self.children = None
        self.data = []
        self.max_items = 100
    
    def insert(self, item):
        if not self.bounds.contains(item):
            return False
            
        if len(self.data) < self.max_items:
            self.data.append(item)
            return True
            
        if not self.children:
            self.subdivide()
            
        for child in self.children:
            if child.insert(item):
                return True
                
    def query(self, bounds):
        results = []
        if not self.bounds.intersects(bounds):
            return results
            
        for item in self.data:
            if bounds.contains(item):
                results.append(item)
                
        if self.children:
            for child in self.children:
                results.extend(child.query(bounds))
                
        return results
```

**Vector Tile Format**
```protobuf
message Tile {
    repeated Layer layers = 3;
}

message Layer {
    required uint32 version = 15 [default = 1];
    required string name = 1;
    repeated Feature features = 2;
    repeated string keys = 3;
    repeated Value values = 4;
    optional uint32 extent = 5 [default = 4096];
}

message Feature {
    optional uint64 id = 1;
    repeated uint32 tags = 2;
    optional GeomType type = 3;
    repeated uint32 geometry = 4;
}
```

### 2. Routing Service

**Graph Representation**
```python
class RoadNetwork:
    def __init__(self):
        self.nodes = {}  # node_id -> (lat, lon)
        self.edges = {}  # edge_id -> (from_node, to_node, distance, attributes)
        self.adjacency = {}  # node_id -> [(neighbor_id, edge_id)]
    
    def add_road(self, from_node, to_node, distance, road_type, speed_limit):
        edge_id = f"{from_node}_{to_node}"
        self.edges[edge_id] = {
            'from': from_node,
            'to': to_node,
            'distance': distance,
            'road_type': road_type,
            'speed_limit': speed_limit,
            'traffic_factor': 1.0
        }
        
        if from_node not in self.adjacency:
            self.adjacency[from_node] = []
        self.adjacency[from_node].append((to_node, edge_id))
```

**Routing Algorithm (Contraction Hierarchies)**
```python
class RoutingEngine:
    def __init__(self, network):
        self.network = network
        self.shortcuts = self.preprocess_network()
    
    def preprocess_network(self):
        # Build contraction hierarchies
        shortcuts = {}
        node_order = self.compute_node_ordering()
        
        for node in node_order:
            # Contract node and add shortcuts
            neighbors = self.network.adjacency[node]
            for n1, e1 in neighbors:
                for n2, e2 in neighbors:
                    if n1 != n2:
                        shortcut = self.compute_shortcut(n1, n2, node)
                        if shortcut:
                            shortcuts[(n1, n2)] = shortcut
        
        return shortcuts
    
    def find_route(self, start, end):
        # Bidirectional Dijkstra with shortcuts
        forward_dist = {start: 0}
        backward_dist = {end: 0}
        forward_heap = [(0, start)]
        backward_heap = [(0, end)]
        meeting_node = None
        best_distance = float('inf')
        
        while forward_heap and backward_heap:
            # Forward search
            if forward_heap:
                dist, node = heappop(forward_heap)
                if node in backward_dist:
                    total = dist + backward_dist[node]
                    if total < best_distance:
                        best_distance = total
                        meeting_node = node
                
                for neighbor, edge_id in self.get_neighbors(node):
                    new_dist = dist + self.get_edge_weight(edge_id)
                    if neighbor not in forward_dist or new_dist < forward_dist[neighbor]:
                        forward_dist[neighbor] = new_dist
                        heappush(forward_heap, (new_dist, neighbor))
            
            # Similar for backward search...
        
        return self.reconstruct_path(start, end, meeting_node)
```

**Multi-Modal Routing**
```python
class MultiModalRouter:
    def __init__(self):
        self.road_network = RoadNetwork()
        self.transit_network = TransitNetwork()
        self.walking_network = WalkingNetwork()
    
    def find_route(self, start, end, modes=['driving', 'transit', 'walking']):
        routes = []
        
        if 'driving' in modes:
            routes.append(self.road_network.find_route(start, end))
        
        if 'transit' in modes:
            # Find nearby transit stops
            start_stops = self.find_nearby_stops(start)
            end_stops = self.find_nearby_stops(end)
            
            for s_stop in start_stops:
                for e_stop in end_stops:
                    transit_route = self.transit_network.find_route(s_stop, e_stop)
                    if transit_route:
                        # Add walking segments
                        walk_to = self.walking_network.find_route(start, s_stop)
                        walk_from = self.walking_network.find_route(e_stop, end)
                        routes.append(walk_to + transit_route + walk_from)
        
        return self.select_best_route(routes)
```

### 3. Search Service

**Geocoding Pipeline**
```python
class GeocodingService:
    def __init__(self):
        self.address_index = self.build_address_index()
        self.place_index = self.build_place_index()
        self.fuzzy_matcher = FuzzyMatcher()
    
    def geocode(self, query):
        # Parse query
        parsed = self.parse_address(query)
        
        # Try exact match
        exact_match = self.exact_match(parsed)
        if exact_match:
            return exact_match
        
        # Try fuzzy match
        candidates = self.fuzzy_search(query)
        
        # Rank candidates
        ranked = self.rank_results(candidates, parsed)
        
        return ranked[0] if ranked else None
    
    def reverse_geocode(self, lat, lon):
        # Find nearest address points
        nearby = self.spatial_index.nearest(lat, lon, k=10)
        
        # Build address from components
        return self.build_address(nearby[0])
```

**POI Search**
```python
class POISearch:
    def __init__(self):
        self.inverted_index = InvertedIndex()
        self.spatial_index = RTree()
        self.category_tree = CategoryTree()
    
    def search(self, query, location, radius):
        # Text search
        text_matches = self.inverted_index.search(query)
        
        # Spatial filter
        spatial_matches = self.spatial_index.search_radius(
            location.lat, location.lon, radius
        )
        
        # Intersect results
        results = text_matches.intersection(spatial_matches)
        
        # Rank by relevance and distance
        ranked = self.rank_results(results, query, location)
        
        return ranked[:20]
    
    def rank_results(self, results, query, location):
        scores = []
        for poi in results:
            score = 0
            score += self.text_relevance(poi, query) * 0.4
            score += self.distance_decay(poi, location) * 0.3
            score += self.popularity_score(poi) * 0.2
            score += self.rating_score(poi) * 0.1
            scores.append((score, poi))
        
        return [poi for score, poi in sorted(scores, reverse=True)]
```

### 4. Traffic Service

**Real-Time Traffic Processing**
```python
class TrafficProcessor:
    def __init__(self):
        self.road_segments = {}
        self.traffic_model = TrafficPredictionModel()
    
    def process_gps_probe(self, probe):
        # Map match to road segment
        segment = self.map_match(probe.lat, probe.lon)
        
        # Calculate speed
        if probe.device_id in self.last_position:
            last = self.last_position[probe.device_id]
            speed = self.calculate_speed(last, probe)
            
            # Update segment speed
            self.update_segment_speed(segment, speed)
        
        self.last_position[probe.device_id] = probe
    
    def update_segment_speed(self, segment_id, speed):
        if segment_id not in self.road_segments:
            self.road_segments[segment_id] = RoadSegment()
        
        segment = self.road_segments[segment_id]
        segment.add_speed_sample(speed)
        
        # Update traffic color
        avg_speed = segment.get_average_speed()
        free_flow_speed = segment.free_flow_speed
        
        if avg_speed > 0.8 * free_flow_speed:
            segment.traffic_color = 'green'
        elif avg_speed > 0.5 * free_flow_speed:
            segment.traffic_color = 'yellow'
        else:
            segment.traffic_color = 'red'
```

**Traffic Prediction**
```python
class TrafficPredictionModel:
    def predict_traffic(self, segment_id, future_time):
        # Get historical patterns
        historical = self.get_historical_pattern(
            segment_id,
            future_time.weekday(),
            future_time.hour
        )
        
        # Get current conditions
        current = self.get_current_traffic(segment_id)
        
        # Apply ML model
        features = self.extract_features(historical, current, future_time)
        prediction = self.model.predict(features)
        
        return prediction
```

### 5. Map Rendering

**Tile Generation Pipeline**
```python
class TileGenerator:
    def __init__(self):
        self.vector_data = VectorDataStore()
        self.style_rules = StyleRules()
        self.cache = TileCache()
    
    def generate_tile(self, z, x, y):
        # Check cache
        cached = self.cache.get(z, x, y)
        if cached:
            return cached
        
        # Get tile bounds
        bounds = self.get_tile_bounds(z, x, y)
        
        # Query vector data
        features = self.vector_data.query(bounds, z)
        
        # Apply styling
        styled_features = self.apply_styles(features, z)
        
        # Render to image
        image = self.render_features(styled_features, z)
        
        # Cache result
        self.cache.put(z, x, y, image)
        
        return image
    
    def apply_styles(self, features, zoom):
        styled = []
        for feature in features:
            style = self.style_rules.get_style(
                feature.type,
                feature.properties,
                zoom
            )
            if style:  # Some features hidden at certain zooms
                styled.append((feature, style))
        return styled
```

**Progressive Loading**
```javascript
class MapRenderer {
    constructor(container) {
        this.container = container;
        this.tileCache = new Map();
        this.loadingTiles = new Set();
    }
    
    async loadTile(z, x, y) {
        const key = `${z}/${x}/${y}`;
        
        // Return cached tile
        if (this.tileCache.has(key)) {
            return this.tileCache.get(key);
        }
        
        // Prevent duplicate loads
        if (this.loadingTiles.has(key)) {
            return;
        }
        
        this.loadingTiles.add(key);
        
        try {
            // Load low-res placeholder first
            const placeholder = await this.loadLowResTile(z, x, y);
            this.renderTile(placeholder, x, y);
            
            // Load full resolution
            const tile = await fetch(`/tiles/${z}/${x}/${y}.png`);
            const blob = await tile.blob();
            const image = await createImageBitmap(blob);
            
            this.tileCache.set(key, image);
            this.renderTile(image, x, y);
        } finally {
            this.loadingTiles.delete(key);
        }
    }
}
```

## Data Storage Design

### Spatial Database (PostGIS)
```sql
-- Road network
CREATE TABLE roads (
    id BIGSERIAL PRIMARY KEY,
    geometry GEOMETRY(LINESTRING, 4326),
    name TEXT,
    road_type VARCHAR(50),
    speed_limit INTEGER,
    one_way BOOLEAN
);
CREATE INDEX idx_roads_geom ON roads USING GIST(geometry);

-- Points of Interest
CREATE TABLE pois (
    id BIGSERIAL PRIMARY KEY,
    location GEOMETRY(POINT, 4326),
    name TEXT,
    category VARCHAR(100),
    address TEXT,
    rating DECIMAL(2,1),
    review_count INTEGER
);
CREATE INDEX idx_pois_location ON pois USING GIST(location);
CREATE INDEX idx_pois_name ON pois USING GIN(to_tsvector('english', name));
```

### Graph Database (for routing)
```
Node properties:
- id: unique identifier
- lat, lon: coordinates
- type: intersection, highway_ramp, etc.

Edge properties:
- from_node, to_node
- distance: meters
- travel_time: seconds
- road_name
- restrictions: turn restrictions, time-based
```

### Time Series Database (for traffic)
```
Table: traffic_speeds
Dimensions:
- segment_id
- timestamp
- source (gps, sensor, prediction)

Metrics:
- speed_mph
- sample_count
- confidence

Retention:
- Raw: 1 week
- 5-min aggregates: 1 month
- Hourly aggregates: 1 year
```

## Optimizations

### 1. Tile Caching Strategy
```
Browser Cache:
- Static tiles: 1 week
- Traffic tiles: 5 minutes

CDN Cache:
- Popular areas: Pre-generated
- Long tail: Generated on demand
- Multiple resolutions: Store 256x256 and 512x512

Server Cache:
- Vector tiles: 1 hour
- Rendered tiles: 1 day
- Route results: 10 minutes
```

### 2. Data Compression
```python
def compress_route(route):
    # Polyline encoding for coordinates
    encoded_path = polyline.encode(route.path)
    
    # Delta encoding for timestamps
    compressed_times = delta_encode(route.times)
    
    # Dictionary compression for instructions
    instruction_dict = build_instruction_dictionary()
    compressed_instructions = compress_with_dict(
        route.instructions,
        instruction_dict
    )
    
    return {
        'path': encoded_path,
        'times': compressed_times,
        'instructions': compressed_instructions
    }
```

### 3. Precomputation
- Contraction hierarchies for routing
- Pre-rendered popular tiles
- Cached common routes
- Preprocessed address data

## Challenges and Solutions

### 1. Map Updates
**Challenge**: Keeping maps current with real-world changes
**Solution**:
- Crowdsourced updates (Map Maker)
- Satellite imagery analysis
- Government data feeds
- Street View car data

### 2. Offline Support
**Challenge**: Maps without internet connection
**Solution**:
- Regional map downloads
- Vector tiles for smaller size
- Compressed routing graphs
- Cached search index

### 3. Location Privacy
**Challenge**: Protecting user location data
**Solution**:
- Client-side routing when possible
- Differential privacy for analytics
- Ephemeral location data
- Opt-in location history

### 4. Global Scale
**Challenge**: Different map data quality worldwide
**Solution**:
- Multiple data sources
- Community contributions
- Satellite imagery fallback
- Progressive enhancement

## Monitoring and Analytics

### Key Metrics
```
Performance:
- Tile load time: p99 < 200ms
- Route calculation: p99 < 1s
- Search latency: p99 < 300ms
- GPS accuracy: < 5 meters

Reliability:
- API success rate: > 99.9%
- Tile cache hit rate: > 80%
- Route accuracy: > 95%

Usage:
- Daily active users
- Routes calculated per day
- Searches per day
- Map tiles served
```

### Analytics Pipeline
```python
class MapAnalytics:
    def track_event(self, event):
        # Real-time processing
        self.stream_processor.process(event)
        
        # Batch analytics
        self.event_store.append(event)
        
        # Update dashboards
        if event.type == 'route_request':
            self.update_routing_metrics(event)
        elif event.type == 'search':
            self.update_search_metrics(event)
```

## Security Considerations

### API Security
- API key authentication
- Rate limiting per key
- Request signing for enterprise
- IP-based restrictions

### Data Protection
- Encrypted transport (HTTPS)
- Encrypted storage for sensitive data
- Access control for map edits
- Audit logging

## Future Enhancements

### Near-term
1. **Indoor Mapping**: Malls, airports, stations
2. **AR Navigation**: Camera-based directions
3. **Predictive Routing**: ML-based ETA
4. **Eco-Friendly Routes**: Fuel-efficient paths

### Long-term
1. **Autonomous Vehicle Maps**: HD maps with lane-level detail
2. **3D City Models**: Photorealistic rendering
3. **Real-time Events**: Accidents, construction, weather
4. **Personalized Maps**: User preference learning

## Interview Tips

1. **Start with Core**: Focus on maps, search, and routing first
2. **Consider Scale**: Billions of users, global coverage
3. **Think Spatially**: Spatial indexes, tile systems
4. **Real-time Aspects**: Traffic and location updates
5. **Optimize Bandwidth**: Compression and caching crucial

## Common Follow-up Questions

1. **"How would you handle real-time location sharing?"**
   - WebSocket connections for live updates
   - Efficient location compression
   - Privacy controls and encryption

2. **"How do you ensure map data accuracy?"**
   - Multiple data sources validation
   - Community reporting system
   - Machine learning for anomaly detection

3. **"How would you implement offline maps?"**
   - Vector tiles for smaller downloads
   - Regional packaging
   - Incremental updates

4. **"How do you handle different map projections?"**
   - Web Mercator for display
   - WGS84 for GPS coordinates
   - On-the-fly reprojection
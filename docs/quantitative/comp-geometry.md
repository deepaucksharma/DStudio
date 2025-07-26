# Computational Geometry for Distributed Systems

## Overview

Computational geometry provides essential algorithms for spatial data processing in distributed systems, from geospatial queries to load balancing in multi-dimensional spaces.

## Core Concepts

### Spatial Data Structures

**Point Location:**
- Given point P and regions R₁...Rₙ
- Find region Rᵢ containing P
- Applications: geo-sharding, routing

**Range Queries:**
- Find all points in rectangle/circle
- Nearest neighbor search
- Applications: proximity services

### Complexity Bounds

| Operation | Naive | Optimized |
|-----------|-------|-----------|
| Point location | O(n) | O(log n) |
| Range query | O(n) | O(k + log n) |
| Nearest neighbor | O(n) | O(log n) |
| Convex hull | O(n²) | O(n log n) |


## Geometric Algorithms

### Voronoi Diagrams

**Definition:**
```
Voronoi(pᵢ) = {x : ||x - pᵢ|| ≤ ||x - pⱼ|| ∀j ≠ i}
```

**Properties:**
- Partitions space into n regions
- Each region has one "owner"
- Dual of Delaunay triangulation

**Applications:**
- Service area assignment
- Load balancing
- Cache placement

### R-Trees

**Structure:**
```
Minimum Bounding Rectangle (MBR)
Node capacity: M entries
Minimum fill: m = M/2
```

**Insert complexity:** O(log n)
**Query complexity:** O(k + log n)

**Variants:**
- R*-tree: optimized splits
- R+-tree: no overlapping
- Hilbert R-tree: space-filling curves

### KD-Trees

**Construction:**
```python
def build_kdtree(points, depth=0):
    axis = depth % k  # k dimensions
    points.sort(key=lambda p: p[axis])
    median = len(points) // 2
    
    return Node(
        point=points[median],
        left=build_kdtree(points[:median], depth+1),
        right=build_kdtree(points[median+1:], depth+1)
    )
```

**Performance:**
- Build: O(n log n)
- Search: O(log n) average
- Worst case: O(n^(1-1/k))

## Geospatial Indexing

### Geohashing

**Encoding:**
```
1. Interleave latitude/longitude bits
2. Convert to base-32 string
3. Precision = string length
```

**Properties:**
- Hierarchical (prefixes)
- Z-order curve mapping
- Variable precision

**Error bounds:**
```
Precision | Error (km)
----------|------------
5 chars   | ±2.4
6 chars   | ±0.61
7 chars   | ±0.076
8 chars   | ±0.019
```

### H3 Hexagonal Grid

**Advantages over squares:**
- Uniform adjacency (6 neighbors)
- Less distortion
- Better for movement

**Resolution table:**
```
Level | Edge Length | Area
------|-------------|------
0     | 1107 km     | 4.25M km²
5     | 8.5 km      | 252 km²
10    | 66 m        | 15000 m²
15    | 0.5 m       | 0.9 m²
```

### S2 Geometry

**Sphere to cube projection:**
1. Project sphere → cube faces
2. Quadtree on each face
3. Hilbert curve ordering

**Cell ID structure:**
```
Face (3 bits) + Position (60 bits) + Sentinel (1 bit)
```

**Coverage algorithms:**
```
RegionCoverer.GetCovering(region, min_level, max_level)
Returns: Set of S2 cells covering region
```

## Distance Calculations

### Haversine Distance

**Formula:**
```
a = sin²(Δφ/2) + cos(φ₁)×cos(φ₂)×sin²(Δλ/2)
c = 2×atan2(√a, √(1-a))
d = R×c
```
Where R = Earth radius (6371 km)

**Error:** ~0.3% (assumes sphere)

### Vincenty's Formula

**More accurate (ellipsoid):**
- Forward: Given point, bearing, distance → destination
- Inverse: Given two points → distance, bearing
- Error: ~0.5mm

### Manhattan Distance

**For grid systems:**
```
d = |x₂ - x₁| + |y₂ - y₁|
```

**Applications:**
- City block distance
- Network hops
- Taxi routing

## Distributed Geometric Algorithms

### Spatial Partitioning

**Grid-based:**
```
cell_x = floor(x / cell_size)
cell_y = floor(y / cell_size)
partition = hash(cell_x, cell_y) % num_partitions
```

**Tree-based:**
- Distribute subtrees to nodes
- Replication at boundaries
- Dynamic rebalancing

### Parallel Convex Hull

**Divide and conquer:**
1. Partition points among nodes
2. Local convex hulls
3. Merge hulls recursively

**Complexity:**
- Sequential: O(n log n)
- Parallel: O(n log n / p + log² p)

### Distributed k-NN

**Approach 1: Replicated index**
- Full index on each node
- Query any node
- Space: O(n) per node

**Approach 2: Partitioned index**
- Spatial partitioning
- Query multiple partitions
- Aggregate results

## Load Balancing

### Space-Filling Curves

**Hilbert curve:**
```
Maps: 2D → 1D preserving locality
Order: 2^n × 2^n grid
Distance preservation: Good
```

**Z-order (Morton):**
```
Interleave binary coordinates
Simple computation
Distance preservation: Moderate
```

**Applications:**
- Range partitioning
- Cache-friendly layouts
- Distributed sorting

### Consistent Hashing with Geometry

**Virtual nodes on circle:**
```
Position = hash(node_id + replica) / 2^32 × 2π
Responsibility = arc to next node
Load = arc_length / (2π)
```

**Multi-dimensional:**
- Hash to k-dimensional space
- Voronoi regions for ownership
- Nearest neighbor for routing

## Real-World Applications

### Uber H3

```python
# Get hexagons within radius
origin = h3.geo_to_h3(lat, lng, resolution=9)
radius_hexes = h3.k_ring(origin, k=2)

# Cover polygon
polygon_hexes = h3.polyfill(polygon, resolution=9)
```

### MongoDB Geospatial

**2dsphere index:**
```javascript
db.places.createIndex({ location: "2dsphere" })

// Find nearby
db.places.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [lng, lat] },
      $maxDistance: 1000
    }
  }
})
```

### PostGIS Operations

```sql
-- Point in polygon
SELECT * FROM regions 
WHERE ST_Contains(geometry, ST_Point(lng, lat));

-- K nearest neighbors
SELECT * FROM locations
ORDER BY geometry <-> ST_Point(lng, lat)
LIMIT k;
```

## Performance Optimization

### Spatial Approximations

**Bounding box pre-filter:**
```
1. Check bounding box (cheap)
2. If passes, check exact geometry
3. 10-100x speedup for complex shapes
```

**Grid acceleration:**
```
Precompute: point → grid_cell
Query: check only relevant cells
Speedup: O(n) → O(k)
```

### Caching Strategies

**Tile-based caching:**
```
TileID = (zoom, x, y)
Cache key = hash(TileID)
TTL = f(zoom_level)
```

**Hot spot detection:**
```
Access frequency heatmap
Adaptive resolution
Prefetch adjacent tiles
```

## Advanced Topics

### Distributed Triangulation

**Delaunay triangulation:**
- Partition with overlap
- Local triangulation
- Merge and cleanup

**Applications:**
- Terrain modeling
- Mesh generation
- Interpolation

### Geometric Streaming

**Sliding window:**
```
Maintain spatial index for last N points
Update incrementally
Space: O(N)
Update: O(log N)
```

**Applications:**
- Real-time tracking
- Trajectory analysis
- Anomaly detection

### Uncertain Geometry

**Probability regions:**
```
P(point in region) = ∫∫ p(x,y) dx dy
```

**Applications:**
- GPS uncertainty
- Sensor fusion
- Prediction regions

## Related Topics

- [Spatial Databases](storage-engines.md)
- [Consistent Hashing](case-studies/consistent-hashing)
- [Location Services](case-studies/proximity-service)
- [Load Balancing](patterns/load-balancing)
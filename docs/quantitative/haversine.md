# Haversine Formula and Geospatial Calculations

## Overview

The Haversine formula calculates the great-circle distance between two points on a sphere, essential for location-based services in distributed systems. This page covers the mathematics, implementation details, and optimization strategies.

## The Haversine Formula

### Mathematical Definition

For two points on a sphere:
- Point 1: (φ₁, λ₁) - latitude, longitude in radians
- Point 2: (φ₂, λ₂) - latitude, longitude in radians

```
a = sin²((φ₂ - φ₁)/2) + cos(φ₁) × cos(φ₂) × sin²((λ₂ - λ₁)/2)
c = 2 × atan2(√a, √(1-a))
d = R × c
```

Where:
- R = Earth's radius (6,371 km mean)
- d = distance in km

### Implementation

```python
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    
    # Convert to radians
    φ1 = math.radians(lat1)
    φ2 = math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = math.sin(Δφ/2)**2 + \
        math.cos(φ1) * math.cos(φ2) * \
        math.sin(Δλ/2)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c
```

## Accuracy Considerations

### Earth Model Assumptions

**Sphere vs Ellipsoid:**
- Haversine assumes perfect sphere
- Earth is oblate ellipsoid
- Error: up to 0.3% (≈300m per 100km)

**Radius variations:**
- Equatorial: 6,378.137 km
- Polar: 6,356.752 km
- Mean: 6,371.0 km

### When Haversine is Sufficient

✅ **Use Haversine for:**
- Distances < 1000 km
- Accuracy ±1 km acceptable
- Performance critical
- Many calculations needed

❌ **Don't use for:**
- Surveying/navigation
- Polar regions
- Very long distances
- Legal boundaries

## Optimizations

### Precomputation

**Store radians:**
```sql
ALTER TABLE locations 
ADD COLUMN lat_rad DOUBLE,
ADD COLUMN lon_rad DOUBLE;

UPDATE locations 
SET lat_rad = RADIANS(latitude),
    lon_rad = RADIANS(longitude);
```

**Precompute trigonometry:**
```sql
ALTER TABLE locations
ADD COLUMN cos_lat DOUBLE,
ADD COLUMN sin_lat DOUBLE;

UPDATE locations
SET cos_lat = COS(lat_rad),
    sin_lat = SIN(lat_rad);
```

### Bounding Box Filter

**Quick rejection test:**
```python
def bounding_box(center_lat, center_lon, radius_km):
    # Degrees per km (approximate)
    lat_degree = radius_km / 111.0
    lon_degree = radius_km / (111.0 * math.cos(math.radians(center_lat)))
    
    return {
        'min_lat': center_lat - lat_degree,
        'max_lat': center_lat + lat_degree,
        'min_lon': center_lon - lon_degree,
        'max_lon': center_lon + lon_degree
    }
```

**SQL query:**
```sql
-- First filter by bounding box (uses index)
SELECT * FROM locations
WHERE latitude BETWEEN :min_lat AND :max_lat
  AND longitude BETWEEN :min_lon AND :max_lon
  AND haversine(:center_lat, :center_lon, latitude, longitude) <= :radius;
```

### Approximations for Small Distances

**Equirectangular approximation:**
```python
def equirectangular(lat1, lon1, lat2, lon2):
    R = 6371
    x = (lon2 - lon1) * math.cos((lat1 + lat2) / 2)
    y = lat2 - lat1
    return R * math.sqrt(x*x + y*y) * math.pi / 180
```

**Error analysis:**
- < 1 km: negligible error
- < 10 km: < 0.1% error
- < 100 km: < 1% error

## Database Implementations

### PostgreSQL with PostGIS

```sql
-- Using geography type (automatic)
SELECT ST_Distance(
    location::geography,
    ST_Point(-73.9857, 40.7484)::geography
) AS distance_meters
FROM places;

-- Custom Haversine function
CREATE FUNCTION haversine(lat1 float, lon1 float, lat2 float, lon2 float)
RETURNS float AS $$
DECLARE
    R constant float := 6371;
    rad constant float := 0.017453292519943295;
    dlat float;
    dlon float;
    a float;
    c float;
BEGIN
    dlat := (lat2 - lat1) * rad;
    dlon := (lon2 - lon1) * rad;
    a := sin(dlat/2)^2 + cos(lat1*rad) * cos(lat2*rad) * sin(dlon/2)^2;
    c := 2 * atan2(sqrt(a), sqrt(1-a));
    RETURN R * c;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

### MySQL

```sql
CREATE FUNCTION haversine(lat1 DOUBLE, lon1 DOUBLE, lat2 DOUBLE, lon2 DOUBLE)
RETURNS DOUBLE
DETERMINISTIC
BEGIN
    DECLARE R DOUBLE DEFAULT 6371;
    DECLARE dLat DOUBLE;
    DECLARE dLon DOUBLE;
    DECLARE a DOUBLE;
    DECLARE c DOUBLE;
    
    SET dLat = RADIANS(lat2 - lat1);
    SET dLon = RADIANS(lon2 - lon1);
    SET a = SIN(dLat/2) * SIN(dLat/2) + 
            COS(RADIANS(lat1)) * COS(RADIANS(lat2)) * 
            SIN(dLon/2) * SIN(dLon/2);
    SET c = 2 * ATAN2(SQRT(a), SQRT(1-a));
    
    RETURN R * c;
END;
```

### MongoDB

```javascript
db.places.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-73.9857, 40.7484] },
      distanceField: "distance",
      spherical: true,
      distanceMultiplier: 0.001  // Convert to km
    }
  }
]);
```

## Performance Optimization

### Vectorized Calculations

**NumPy implementation:**
```python
import numpy as np

def haversine_vectorized(lat1, lon1, lat2_array, lon2_array):
    R = 6371
    
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2_array)
    lon2_rad = np.radians(lon2_array)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = np.sin(dlat/2)**2 + \
        np.cos(lat1_rad) * np.cos(lat2_rad) * \
        np.sin(dlon/2)**2
    
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    
    return R * c
```

### Spatial Indexing

**Grid-based index:**
```python
def get_grid_cell(lat, lon, cell_size_km=10):
    # Approximate degrees per km
    lat_per_km = 1 / 111.0
    lon_per_km = 1 / (111.0 * math.cos(math.radians(lat)))
    
    cell_lat = int(lat / (cell_size_km * lat_per_km))
    cell_lon = int(lon / (cell_size_km * lon_per_km))
    
    return f"{cell_lat},{cell_lon}"
```

**Query optimization:**
```python
def find_nearby(center_lat, center_lon, radius_km, locations):
    # 1. Find relevant grid cells
    cells = get_affected_cells(center_lat, center_lon, radius_km)
    
    # 2. Get candidates from those cells
    candidates = []
    for cell in cells:
        candidates.extend(grid_index[cell])
    
    # 3. Exact distance filter
    results = []
    for loc in candidates:
        dist = haversine(center_lat, center_lon, loc.lat, loc.lon)
        if dist <= radius_km:
            results.append((loc, dist))
    
    return sorted(results, key=lambda x: x[1])
```

## Alternative Formulas

### Vincenty's Formula

**More accurate for ellipsoid:**
```python
def vincenty(lat1, lon1, lat2, lon2):
    # WGS-84 ellipsoid parameters
    a = 6378137.0  # Semi-major axis
    f = 1/298.257223563  # Flattening
    b = (1 - f) * a  # Semi-minor axis
    
    # ... (complex iterative calculation)
    # Error: ~0.5mm
    # 10-100x slower than Haversine
```

### Spherical Law of Cosines

**Simpler but less stable:**
```python
def spherical_cosines(lat1, lon1, lat2, lon2):
    R = 6371
    φ1 = math.radians(lat1)
    φ2 = math.radians(lat2)
    Δλ = math.radians(lon2 - lon1)
    
    return R * math.acos(
        math.sin(φ1) * math.sin(φ2) +
        math.cos(φ1) * math.cos(φ2) * math.cos(Δλ)
    )
```

**Issues:**
- Numerical instability for small distances
- acos domain errors possible

## Distributed Computing

### MapReduce Pattern

```python
# Map: Compute distances
def map_distances(center, locations):
    for loc in locations:
        dist = haversine(center.lat, center.lon, loc.lat, loc.lon)
        if dist <= max_radius:
            yield (dist, loc)

# Reduce: Sort and limit
def reduce_nearest(distances, k):
    return sorted(distances)[:k]
```

### Parallel Processing

```python
from multiprocessing import Pool

def parallel_haversine(center, locations, num_workers=4):
    chunk_size = len(locations) // num_workers
    chunks = [locations[i:i+chunk_size] 
              for i in range(0, len(locations), chunk_size)]
    
    with Pool(num_workers) as pool:
        results = pool.starmap(
            haversine_batch,
            [(center, chunk) for chunk in chunks]
        )
    
    return merge_results(results)
```

## Real-World Applications

### Ride-Sharing

```python
def find_nearby_drivers(rider_lat, rider_lon, max_distance_km=5):
    # Use geohash for initial filter
    geohash_precision = distance_to_geohash_precision(max_distance_km)
    rider_geohash = geohash.encode(rider_lat, rider_lon, geohash_precision)
    
    # Query nearby geohashes
    nearby_hashes = geohash.neighbors(rider_geohash)
    nearby_hashes.append(rider_geohash)
    
    # Get drivers and calculate exact distances
    drivers = []
    for gh in nearby_hashes:
        for driver in drivers_by_geohash[gh]:
            dist = haversine(rider_lat, rider_lon, driver.lat, driver.lon)
            if dist <= max_distance_km:
                drivers.append((driver, dist))
    
    return sorted(drivers, key=lambda x: x[1])
```

### Geofencing

```python
def check_geofence(lat, lon, fence_center_lat, fence_center_lon, radius_km):
    distance = haversine(lat, lon, fence_center_lat, fence_center_lon)
    
    if distance <= radius_km * 0.9:
        return "INSIDE"
    elif distance <= radius_km * 1.1:
        return "BOUNDARY"
    else:
        return "OUTSIDE"
```

## Common Pitfalls

### Coordinate Order

```python
# WRONG: Many APIs use lon, lat order
distance = haversine(lon1, lat1, lon2, lat2)  # ❌

# CORRECT: Mathematical convention is lat, lon
distance = haversine(lat1, lon1, lat2, lon2)  # ✅
```

### Unit Confusion

```python
# Ensure consistent units
def safe_haversine(lat1, lon1, lat2, lon2, unit='km'):
    d_km = haversine(lat1, lon1, lat2, lon2)
    
    if unit == 'km':
        return d_km
    elif unit == 'mi':
        return d_km * 0.621371
    elif unit == 'm':
        return d_km * 1000
    else:
        raise ValueError(f"Unknown unit: {unit}")
```

### Performance vs Accuracy

```python
def adaptive_distance(lat1, lon1, lat2, lon2, max_error_km=0.1):
    # Quick check: are points close?
    dlat = abs(lat2 - lat1)
    dlon = abs(lon2 - lon1)
    
    if dlat < 0.1 and dlon < 0.1:
        # Use fast approximation for nearby points
        return equirectangular(lat1, lon1, lat2, lon2)
    else:
        # Use Haversine for longer distances
        return haversine(lat1, lon1, lat2, lon2)
```

## Related Topics

- [Computational Geometry](comp-geometry.md)
- Spatial Indexing (Coming Soon)
- [Location Services](/case-studies/proximity-service)
- [Performance Optimization](performance-modeling.md)
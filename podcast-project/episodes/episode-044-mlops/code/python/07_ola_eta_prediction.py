#!/usr/bin/env python3
"""
Ola ETA Prediction System - MLOps Episode 44
Production-ready ETA prediction with real-time traffic and ML models

Author: Claude Code
Context: Real-time ETA prediction system like Ola's production system
"""

import json
import time
import uuid
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import logging
import math
import threading
from collections import defaultdict, deque
import requests
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VehicleType(Enum):
    """Vehicle types in Ola"""
    MICRO = "micro"
    MINI = "mini"
    PRIME = "prime"
    AUTO = "auto"
    BIKE = "bike"

class TrafficCondition(Enum):
    """Traffic conditions"""
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    JAM = "jam"

class WeatherCondition(Enum):
    """Weather conditions"""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    FOG = "fog"

@dataclass
class Location:
    """Geographic location"""
    latitude: float
    longitude: float
    address: Optional[str] = None
    landmark: Optional[str] = None

@dataclass
class RideRequest:
    """Ride booking request"""
    request_id: str
    user_id: str
    pickup_location: Location
    drop_location: Location
    vehicle_type: VehicleType
    request_time: datetime
    estimated_fare: float
    priority: int = 1

@dataclass
class TrafficData:
    """Real-time traffic information"""
    route_id: str
    segment_length_km: float
    current_speed_kmh: float
    normal_speed_kmh: float
    traffic_condition: TrafficCondition
    congestion_factor: float
    timestamp: datetime

@dataclass
class WeatherData:
    """Weather information"""
    location: Location
    temperature: float
    humidity: float
    weather_condition: WeatherCondition
    wind_speed: float
    visibility_km: float
    timestamp: datetime

@dataclass
class ETAPrediction:
    """ETA prediction result"""
    request_id: str
    predicted_eta_minutes: float
    confidence_score: float
    distance_km: float
    base_travel_time: float
    traffic_delay: float
    weather_impact: float
    model_version: str
    prediction_time_ms: float
    route_segments: List[Dict[str, Any]]
    timestamp: datetime

class OlaETAPredictor:
    """
    Production ETA Prediction System for Ola-style ride hailing
    Mumbai me sabse accurate ETA prediction!
    """
    
    def __init__(self, db_path: str = "ola_eta_prediction.db"):
        self.db_path = db_path
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        
        # Real-time data caches
        self.traffic_cache: Dict[str, TrafficData] = {}
        self.weather_cache: Dict[str, WeatherData] = {}
        self.historical_trips: deque = deque(maxlen=10000)
        self.route_cache: Dict[str, Dict] = {}
        
        # Mumbai specific data
        self.mumbai_landmarks = {
            'bandra': (19.0596, 72.8295),
            'andheri': (19.1136, 72.8697),
            'churchgate': (18.9322, 72.8264),
            'dadar': (19.0178, 72.8478),
            'kurla': (19.0728, 72.8826),
            'powai': (19.1176, 72.9060),
            'ghatkopar': (19.0864, 72.9081),
            'thane': (19.2183, 72.9781),
            'navi_mumbai': (19.0330, 73.0297),
            'bkc': (19.0646, 72.8679)  # Bandra Kurla Complex
        }
        
        # Traffic patterns by hour and day
        self.traffic_patterns = self._load_traffic_patterns()
        
        self.lock = threading.Lock()
        self._init_database()
        self._load_models()
    
    def _init_database(self):
        """Initialize ETA prediction database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS ride_requests (
                    request_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    pickup_lat REAL NOT NULL,
                    pickup_lon REAL NOT NULL,
                    pickup_address TEXT,
                    drop_lat REAL NOT NULL,
                    drop_lon REAL NOT NULL,
                    drop_address TEXT,
                    vehicle_type TEXT NOT NULL,
                    request_time TEXT NOT NULL,
                    estimated_fare REAL,
                    priority INTEGER DEFAULT 1,
                    actual_pickup_time TEXT,
                    actual_eta_minutes REAL,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS eta_predictions (
                    prediction_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    predicted_eta_minutes REAL NOT NULL,
                    confidence_score REAL NOT NULL,
                    distance_km REAL NOT NULL,
                    base_travel_time REAL NOT NULL,
                    traffic_delay REAL NOT NULL,
                    weather_impact REAL NOT NULL,
                    model_version TEXT NOT NULL,
                    prediction_time_ms REAL NOT NULL,
                    route_segments TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (request_id) REFERENCES ride_requests (request_id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS traffic_data (
                    traffic_id TEXT PRIMARY KEY,
                    route_id TEXT NOT NULL,
                    segment_length_km REAL NOT NULL,
                    current_speed_kmh REAL NOT NULL,
                    normal_speed_kmh REAL NOT NULL,
                    traffic_condition TEXT NOT NULL,
                    congestion_factor REAL NOT NULL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS historical_trips (
                    trip_id TEXT PRIMARY KEY,
                    pickup_lat REAL NOT NULL,
                    pickup_lon REAL NOT NULL,
                    drop_lat REAL NOT NULL,
                    drop_lon REAL NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    actual_duration_minutes REAL NOT NULL,
                    distance_km REAL NOT NULL,
                    hour_of_day INTEGER NOT NULL,
                    day_of_week INTEGER NOT NULL,
                    weather_condition TEXT,
                    traffic_condition TEXT,
                    completed_at TEXT NOT NULL
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_predictions_request ON eta_predictions (request_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_traffic_route_time ON traffic_data (route_id, timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_trips_location_time ON historical_trips (pickup_lat, pickup_lon, completed_at)')
    
    def _load_traffic_patterns(self) -> Dict[str, Dict[str, float]]:
        """Load Mumbai traffic patterns by hour and day"""
        # Based on Mumbai traffic analysis
        patterns = {
            'weekday': {
                # Hour -> congestion multiplier
                0: 0.3, 1: 0.2, 2: 0.2, 3: 0.2, 4: 0.3, 5: 0.5,
                6: 0.8, 7: 1.5, 8: 2.0, 9: 1.8, 10: 1.3, 11: 1.2,
                12: 1.4, 13: 1.3, 14: 1.2, 15: 1.4, 16: 1.6, 17: 1.8,
                18: 2.2, 19: 2.5, 20: 2.0, 21: 1.5, 22: 1.0, 23: 0.6
            },
            'weekend': {
                0: 0.3, 1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.3,
                6: 0.4, 7: 0.6, 8: 0.8, 9: 1.0, 10: 1.2, 11: 1.4,
                12: 1.5, 13: 1.4, 14: 1.3, 15: 1.2, 16: 1.3, 17: 1.4,
                18: 1.5, 19: 1.6, 20: 1.4, 21: 1.2, 22: 0.9, 23: 0.6
            }
        }
        return patterns
    
    def _load_models(self):
        """Load pre-trained ETA prediction models"""
        try:
            # In production, these would be loaded from model registry
            # For demo, create and train models
            self._train_demo_models()
            logger.info("ETA prediction models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            self._train_demo_models()
    
    def _train_demo_models(self):
        """Train demo ETA prediction models"""
        # Generate sample training data
        training_data = self._generate_training_data(5000)
        
        # Prepare features
        X, y = self._prepare_features(training_data)
        
        # Train models for different vehicle types
        for vehicle_type in VehicleType:
            # Filter data for this vehicle type
            vehicle_mask = X['vehicle_type'] == vehicle_type.value
            if vehicle_mask.sum() < 100:  # Skip if insufficient data
                continue
            
            X_vehicle = X[vehicle_mask]
            y_vehicle = y[vehicle_mask]
            
            # Feature engineering
            feature_columns = [
                'distance_km', 'hour_of_day', 'day_of_week', 'is_weekend',
                'traffic_factor', 'weather_factor', 'pickup_area_congestion',
                'drop_area_congestion', 'historical_avg_speed'
            ]
            
            X_features = X_vehicle[feature_columns]
            
            # Train Random Forest model
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_features, y_vehicle)
            
            # Store model and scaler
            self.models[vehicle_type.value] = model
            
            scaler = StandardScaler()
            scaler.fit(X_features)
            self.scalers[vehicle_type.value] = scaler
        
        logger.info(f"Trained models for {len(self.models)} vehicle types")
    
    def _generate_training_data(self, n_samples: int) -> pd.DataFrame:
        """Generate realistic training data for Mumbai"""
        data = []
        
        mumbai_locations = list(self.mumbai_landmarks.values())
        
        for i in range(n_samples):
            # Random pickup and drop locations in Mumbai
            pickup_lat, pickup_lon = mumbai_locations[np.random.randint(0, len(mumbai_locations))]
            drop_lat, drop_lon = mumbai_locations[np.random.randint(0, len(mumbai_locations))]
            
            # Add some noise to coordinates
            pickup_lat += np.random.normal(0, 0.01)
            pickup_lon += np.random.normal(0, 0.01)
            drop_lat += np.random.normal(0, 0.01)
            drop_lon += np.random.normal(0, 0.01)
            
            # Calculate distance
            distance_km = self._calculate_distance(pickup_lat, pickup_lon, drop_lat, drop_lon)
            
            # Random timestamp in last 6 months
            timestamp = datetime.now() - timedelta(days=np.random.randint(1, 180))
            hour_of_day = timestamp.hour
            day_of_week = timestamp.weekday()
            is_weekend = day_of_week >= 5
            
            # Vehicle type
            vehicle_type = np.random.choice(list(VehicleType)).value
            
            # Traffic and weather factors
            pattern_type = 'weekend' if is_weekend else 'weekday'
            traffic_factor = self.traffic_patterns[pattern_type][hour_of_day]
            weather_factor = np.random.uniform(0.8, 1.2)  # Weather impact
            
            # Base speed by vehicle type
            base_speeds = {
                'micro': 15, 'mini': 18, 'prime': 20, 'auto': 12, 'bike': 25
            }
            base_speed = base_speeds.get(vehicle_type, 18)
            
            # Calculate actual duration with realistic factors
            base_time = (distance_km / base_speed) * 60  # minutes
            traffic_delay = base_time * (traffic_factor - 1) * 0.5
            weather_delay = base_time * (weather_factor - 1) * 0.3
            random_factor = np.random.normal(1.0, 0.1)  # 10% random variation
            
            actual_duration = max(5, (base_time + traffic_delay + weather_delay) * random_factor)
            
            data.append({
                'pickup_lat': pickup_lat,
                'pickup_lon': pickup_lon,
                'drop_lat': drop_lat,
                'drop_lon': drop_lon,
                'vehicle_type': vehicle_type,
                'distance_km': distance_km,
                'hour_of_day': hour_of_day,
                'day_of_week': day_of_week,
                'is_weekend': is_weekend,
                'traffic_factor': traffic_factor,
                'weather_factor': weather_factor,
                'pickup_area_congestion': np.random.uniform(0.5, 2.0),
                'drop_area_congestion': np.random.uniform(0.5, 2.0),
                'historical_avg_speed': base_speed * np.random.uniform(0.8, 1.2),
                'actual_duration_minutes': actual_duration,
                'timestamp': timestamp
            })
        
        return pd.DataFrame(data)
    
    def _prepare_features(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for model training"""
        X = data.drop(['actual_duration_minutes', 'timestamp'], axis=1)
        y = data['actual_duration_minutes']
        return X, y
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _get_current_traffic_factor(self, pickup_location: Location, drop_location: Location, timestamp: datetime) -> float:
        """
        Get current traffic factor for route
        Mumbai me real-time traffic ka factor!
        """
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        is_weekend = day_of_week >= 5
        
        pattern_type = 'weekend' if is_weekend else 'weekday'
        base_factor = self.traffic_patterns[pattern_type][hour]
        
        # Add route-specific adjustments
        route_key = f"{pickup_location.latitude:.3f},{pickup_location.longitude:.3f}-{drop_location.latitude:.3f},{drop_location.longitude:.3f}"
        
        # Check for real-time traffic data
        if route_key in self.traffic_cache:
            traffic_data = self.traffic_cache[route_key]
            if (timestamp - traffic_data.timestamp).total_seconds() < 300:  # 5 minutes fresh
                return traffic_data.congestion_factor
        
        # Add Mumbai-specific congestion for major routes
        congestion_multiplier = 1.0
        
        # Check if route passes through high-congestion areas
        high_congestion_areas = ['bandra', 'andheri', 'dadar', 'kurla']
        for area, (area_lat, area_lon) in self.mumbai_landmarks.items():
            if area in high_congestion_areas:
                # Check if route is near this area
                pickup_dist = self._calculate_distance(pickup_location.latitude, pickup_location.longitude, area_lat, area_lon)
                drop_dist = self._calculate_distance(drop_location.latitude, drop_location.longitude, area_lat, area_lon)
                
                if pickup_dist < 2 or drop_dist < 2:  # Within 2km
                    congestion_multiplier *= 1.2
        
        return base_factor * congestion_multiplier
    
    def _get_weather_impact(self, timestamp: datetime) -> float:
        """Get weather impact on ETA"""
        # Simulate weather impact (in production, use weather API)
        # Mumbai monsoon effect
        month = timestamp.month
        
        if 6 <= month <= 9:  # Monsoon season
            # Higher chance of rain affecting travel
            rain_factor = np.random.choice([1.0, 1.2, 1.5, 2.0], p=[0.4, 0.3, 0.2, 0.1])
        else:
            rain_factor = np.random.choice([1.0, 1.1], p=[0.9, 0.1])
        
        return rain_factor
    
    def predict_eta(self, ride_request: RideRequest) -> ETAPrediction:
        """
        Predict ETA for ride request
        Mumbai me accurate ETA prediction!
        """
        start_time = time.time()
        
        try:
            # Calculate distance
            distance_km = self._calculate_distance(
                ride_request.pickup_location.latitude,
                ride_request.pickup_location.longitude,
                ride_request.drop_location.latitude,
                ride_request.drop_location.longitude
            )
            
            # Extract time features
            hour_of_day = ride_request.request_time.hour
            day_of_week = ride_request.request_time.weekday()
            is_weekend = day_of_week >= 5
            
            # Get traffic and weather factors
            traffic_factor = self._get_current_traffic_factor(
                ride_request.pickup_location,
                ride_request.drop_location,
                ride_request.request_time
            )
            
            weather_factor = self._get_weather_impact(ride_request.request_time)
            
            # Get historical speed for this area
            historical_speed = self._get_historical_speed(
                ride_request.pickup_location,
                ride_request.drop_location,
                hour_of_day,
                day_of_week
            )
            
            # Prepare features for prediction
            features = {
                'distance_km': distance_km,
                'hour_of_day': hour_of_day,
                'day_of_week': day_of_week,
                'is_weekend': int(is_weekend),
                'traffic_factor': traffic_factor,
                'weather_factor': weather_factor,
                'pickup_area_congestion': self._get_area_congestion(ride_request.pickup_location),
                'drop_area_congestion': self._get_area_congestion(ride_request.drop_location),
                'historical_avg_speed': historical_speed
            }
            
            # Get model for vehicle type
            vehicle_type = ride_request.vehicle_type.value
            if vehicle_type not in self.models:
                # Use default model (mini)
                vehicle_type = VehicleType.MINI.value
            
            model = self.models[vehicle_type]
            
            # Create feature vector
            feature_vector = np.array([list(features.values())])
            
            # Predict ETA
            predicted_eta = model.predict(feature_vector)[0]
            
            # Calculate components
            base_speeds = {
                'micro': 15, 'mini': 18, 'prime': 20, 'auto': 12, 'bike': 25
            }
            base_speed = base_speeds.get(ride_request.vehicle_type.value, 18)
            base_travel_time = (distance_km / base_speed) * 60
            
            traffic_delay = base_travel_time * (traffic_factor - 1) * 0.5
            weather_impact = base_travel_time * (weather_factor - 1) * 0.3
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(features, predicted_eta, distance_km)
            
            # Create route segments (simplified)
            route_segments = self._create_route_segments(
                ride_request.pickup_location,
                ride_request.drop_location,
                distance_km
            )
            
            prediction_time_ms = (time.time() - start_time) * 1000
            
            prediction = ETAPrediction(
                request_id=ride_request.request_id,
                predicted_eta_minutes=max(5, predicted_eta),  # Minimum 5 minutes
                confidence_score=confidence_score,
                distance_km=distance_km,
                base_travel_time=base_travel_time,
                traffic_delay=traffic_delay,
                weather_impact=weather_impact,
                model_version="ola_eta_v1.0",
                prediction_time_ms=prediction_time_ms,
                route_segments=route_segments,
                timestamp=datetime.now()
            )
            
            # Store prediction
            self._store_prediction(prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"ETA prediction failed: {e}")
            # Return fallback prediction
            distance_km = self._calculate_distance(
                ride_request.pickup_location.latitude,
                ride_request.pickup_location.longitude,
                ride_request.drop_location.latitude,
                ride_request.drop_location.longitude
            )
            
            fallback_eta = max(10, (distance_km / 15) * 60)  # 15 km/h average
            
            return ETAPrediction(
                request_id=ride_request.request_id,
                predicted_eta_minutes=fallback_eta,
                confidence_score=0.5,
                distance_km=distance_km,
                base_travel_time=fallback_eta,
                traffic_delay=0,
                weather_impact=0,
                model_version="fallback_v1.0",
                prediction_time_ms=0,
                route_segments=[],
                timestamp=datetime.now()
            )
    
    def _get_historical_speed(self, pickup: Location, drop: Location, hour: int, day: int) -> float:
        """Get historical average speed for similar trips"""
        # In production, query historical database
        # For demo, return estimated speed based on time and distance
        
        base_speeds = {
            'morning_peak': 12,   # 7-10 AM
            'day_time': 20,       # 10 AM - 4 PM
            'evening_peak': 10,   # 4-8 PM
            'night': 25          # 8 PM - 7 AM
        }
        
        if 7 <= hour <= 10:
            period = 'morning_peak'
        elif 10 < hour <= 16:
            period = 'day_time'
        elif 16 < hour <= 20:
            period = 'evening_peak'
        else:
            period = 'night'
        
        return base_speeds[period] * (1.2 if day >= 5 else 1.0)  # Weekend bonus
    
    def _get_area_congestion(self, location: Location) -> float:
        """Get congestion factor for specific area"""
        # Check if location is near major congestion points
        congestion_factors = {
            'bandra': 1.8,
            'andheri': 1.6,
            'dadar': 2.0,
            'kurla': 1.7,
            'churchgate': 1.5,
            'thane': 1.4
        }
        
        max_congestion = 1.0
        
        for area, (area_lat, area_lon) in self.mumbai_landmarks.items():
            distance = self._calculate_distance(location.latitude, location.longitude, area_lat, area_lon)
            if distance < 2:  # Within 2km
                area_congestion = congestion_factors.get(area, 1.0)
                max_congestion = max(max_congestion, area_congestion)
        
        return max_congestion
    
    def _calculate_confidence(self, features: Dict[str, float], predicted_eta: float, distance_km: float) -> float:
        """Calculate prediction confidence score"""
        confidence = 0.8  # Base confidence
        
        # Reduce confidence for long distances
        if distance_km > 20:
            confidence -= 0.1
        
        # Reduce confidence for high traffic
        if features['traffic_factor'] > 2.0:
            confidence -= 0.2
        
        # Reduce confidence for extreme weather
        if features['weather_factor'] > 1.5:
            confidence -= 0.1
        
        # Reduce confidence for very short or very long ETAs
        if predicted_eta < 10 or predicted_eta > 120:
            confidence -= 0.1
        
        return max(0.1, min(0.95, confidence))
    
    def _create_route_segments(self, pickup: Location, drop: Location, total_distance: float) -> List[Dict[str, Any]]:
        """Create route segments for detailed ETA breakdown"""
        # Simplified route segmentation
        num_segments = min(5, max(2, int(total_distance / 2)))
        segments = []
        
        lat_step = (drop.latitude - pickup.latitude) / num_segments
        lon_step = (drop.longitude - pickup.longitude) / num_segments
        
        for i in range(num_segments):
            start_lat = pickup.latitude + i * lat_step
            start_lon = pickup.longitude + i * lon_step
            end_lat = pickup.latitude + (i + 1) * lat_step
            end_lon = pickup.longitude + (i + 1) * lon_step
            
            segment_distance = total_distance / num_segments
            estimated_time = (segment_distance / 18) * 60  # 18 km/h average
            
            segments.append({
                'segment_id': i + 1,
                'start_location': {'lat': start_lat, 'lon': start_lon},
                'end_location': {'lat': end_lat, 'lon': end_lon},
                'distance_km': segment_distance,
                'estimated_time_minutes': estimated_time,
                'traffic_condition': 'moderate'
            })
        
        return segments
    
    def _store_prediction(self, prediction: ETAPrediction):
        """Store ETA prediction in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO eta_predictions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(uuid.uuid4()),
                    prediction.request_id,
                    prediction.predicted_eta_minutes,
                    prediction.confidence_score,
                    prediction.distance_km,
                    prediction.base_travel_time,
                    prediction.traffic_delay,
                    prediction.weather_impact,
                    prediction.model_version,
                    prediction.prediction_time_ms,
                    json.dumps(prediction.route_segments),
                    prediction.timestamp.isoformat()
                ))
        except Exception as e:
            logger.error(f"Failed to store prediction: {e}")
    
    def update_actual_eta(self, request_id: str, actual_eta_minutes: float) -> bool:
        """Update with actual ETA for model improvement"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE ride_requests 
                    SET actual_eta_minutes = ?, actual_pickup_time = ?
                    WHERE request_id = ?
                ''', (actual_eta_minutes, datetime.now().isoformat(), request_id))
            
            return True
        except Exception as e:
            logger.error(f"Failed to update actual ETA: {e}")
            return False
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get model performance metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    r.vehicle_type,
                    COUNT(*) as total_predictions,
                    AVG(ABS(p.predicted_eta_minutes - r.actual_eta_minutes)) as mae,
                    AVG(p.confidence_score) as avg_confidence,
                    AVG(p.prediction_time_ms) as avg_prediction_time
                FROM eta_predictions p
                JOIN ride_requests r ON p.request_id = r.request_id
                WHERE r.actual_eta_minutes IS NOT NULL
                GROUP BY r.vehicle_type
            ''')
            
            performance = {}
            for row in cursor.fetchall():
                vehicle_type, total, mae, avg_conf, avg_time = row
                performance[vehicle_type] = {
                    'total_predictions': total,
                    'mean_absolute_error': mae,
                    'average_confidence': avg_conf,
                    'average_prediction_time_ms': avg_time
                }
            
            return performance

def create_sample_ride_requests(n_requests: int = 100) -> List[RideRequest]:
    """
    Create sample ride requests for testing
    Mumbai me realistic ride requests!
    """
    requests = []
    mumbai_locations = {
        'bandra': (19.0596, 72.8295),
        'andheri': (19.1136, 72.8697),
        'churchgate': (18.9322, 72.8264),
        'dadar': (19.0178, 72.8478),
        'kurla': (19.0728, 72.8826),
        'powai': (19.1176, 72.9060),
        'ghatkopar': (19.0864, 72.9081),
        'thane': (19.2183, 72.9781),
        'navi_mumbai': (19.0330, 73.0297),
        'bkc': (19.0646, 72.8679)
    }
    
    location_names = list(mumbai_locations.keys())
    
    for i in range(n_requests):
        # Random pickup and drop locations
        pickup_name = np.random.choice(location_names)
        drop_name = np.random.choice(location_names)
        
        while pickup_name == drop_name:
            drop_name = np.random.choice(location_names)
        
        pickup_lat, pickup_lon = mumbai_locations[pickup_name]
        drop_lat, drop_lon = mumbai_locations[drop_name]
        
        # Add some noise to coordinates
        pickup_lat += np.random.normal(0, 0.005)
        pickup_lon += np.random.normal(0, 0.005)
        drop_lat += np.random.normal(0, 0.005)
        drop_lon += np.random.normal(0, 0.005)
        
        # Random request time (today)
        base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        request_time = base_time + timedelta(
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60)
        )
        
        request = RideRequest(
            request_id=f"req_{i:04d}",
            user_id=f"user_{np.random.randint(1, 1000):04d}",
            pickup_location=Location(pickup_lat, pickup_lon, f"{pickup_name.title()}, Mumbai"),
            drop_location=Location(drop_lat, drop_lon, f"{drop_name.title()}, Mumbai"),
            vehicle_type=np.random.choice(list(VehicleType)),
            request_time=request_time,
            estimated_fare=np.random.uniform(50, 500),
            priority=np.random.randint(1, 4)
        )
        
        requests.append(request)
    
    return requests

def main():
    """
    Demo Ola ETA Prediction System
    Mumbai ke ETA prediction ka demo!
    """
    print("🚗 Starting Ola ETA Prediction System Demo")
    print("=" * 50)
    
    # Initialize ETA predictor
    predictor = OlaETAPredictor("ola_eta_demo.db")
    
    # Create sample ride requests
    print("\n📱 Creating sample ride requests...")
    requests = create_sample_ride_requests(50)
    print(f"Generated {len(requests)} ride requests")
    
    # Predict ETAs
    print("\n🔮 Predicting ETAs...")
    predictions = []
    total_prediction_time = 0
    
    for i, request in enumerate(requests):
        prediction = predictor.predict_eta(request)
        predictions.append(prediction)
        total_prediction_time += prediction.prediction_time_ms
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1} requests...")
    
    # Analyze results
    print(f"\n📊 ETA Prediction Results:")
    print(f"  Total Requests: {len(requests)}")
    print(f"  Average Prediction Time: {total_prediction_time / len(predictions):.2f}ms")
    print(f"  Throughput: {len(predictions) / (total_prediction_time / 1000):.0f} predictions/second")
    
    # Statistics by vehicle type
    vehicle_stats = defaultdict(list)
    for prediction in predictions:
        request = next(r for r in requests if r.request_id == prediction.request_id)
        vehicle_stats[request.vehicle_type.value].append(prediction)
    
    print(f"\n🚙 Statistics by Vehicle Type:")
    for vehicle_type, preds in vehicle_stats.items():
        avg_eta = np.mean([p.predicted_eta_minutes for p in preds])
        avg_confidence = np.mean([p.confidence_score for p in preds])
        avg_distance = np.mean([p.distance_km for p in preds])
        
        print(f"  {vehicle_type.upper()}:")
        print(f"    Average ETA: {avg_eta:.1f} minutes")
        print(f"    Average Distance: {avg_distance:.1f} km")
        print(f"    Average Confidence: {avg_confidence:.3f}")
    
    # Show some example predictions
    print(f"\n🎯 Example ETA Predictions:")
    
    for i, prediction in enumerate(predictions[:5]):
        request = next(r for r in requests if r.request_id == prediction.request_id)
        
        print(f"\n  Request {i + 1}:")
        print(f"    Route: {request.pickup_location.address} → {request.drop_location.address}")
        print(f"    Vehicle: {request.vehicle_type.value}")
        print(f"    Distance: {prediction.distance_km:.1f} km")
        print(f"    Predicted ETA: {prediction.predicted_eta_minutes:.1f} minutes")
        print(f"    Confidence: {prediction.confidence_score:.3f}")
        print(f"    Base Time: {prediction.base_travel_time:.1f} min")
        print(f"    Traffic Delay: {prediction.traffic_delay:.1f} min")
        print(f"    Weather Impact: {prediction.weather_impact:.1f} min")
    
    # Time-based analysis
    print(f"\n⏰ ETA by Time of Day:")
    hour_stats = defaultdict(list)
    
    for prediction in predictions:
        request = next(r for r in requests if r.request_id == prediction.request_id)
        hour = request.request_time.hour
        hour_stats[hour].append(prediction.predicted_eta_minutes)
    
    peak_hours = []
    for hour in sorted(hour_stats.keys()):
        avg_eta = np.mean(hour_stats[hour])
        if avg_eta > 25:  # Consider > 25 min as peak
            peak_hours.append(hour)
        print(f"    {hour:02d}:00 - Average ETA: {avg_eta:.1f} minutes")
    
    print(f"\n🚦 Peak Hours (ETA > 25 min): {peak_hours}")
    
    # Simulate some actual ETAs for performance measurement
    print(f"\n📈 Simulating Model Performance...")
    
    for prediction in predictions[:20]:
        # Simulate actual ETA (with some noise around prediction)
        noise = np.random.normal(0, prediction.predicted_eta_minutes * 0.1)
        actual_eta = max(5, prediction.predicted_eta_minutes + noise)
        predictor.update_actual_eta(prediction.request_id, actual_eta)
    
    # Get performance metrics
    performance = predictor.get_model_performance()
    if performance:
        print(f"\n📊 Model Performance by Vehicle Type:")
        for vehicle_type, metrics in performance.items():
            print(f"  {vehicle_type.upper()}:")
            print(f"    Mean Absolute Error: {metrics['mean_absolute_error']:.2f} minutes")
            print(f"    Average Confidence: {metrics['average_confidence']:.3f}")
            print(f"    Prediction Speed: {metrics['average_prediction_time_ms']:.2f}ms")
    
    print(f"\n✅ ETA prediction demo completed!")
    print("Mumbai me ETA prediction bhi traffic police ki tarah accurate!")

if __name__ == "__main__":
    main()
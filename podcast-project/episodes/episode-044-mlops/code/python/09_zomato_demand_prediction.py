#!/usr/bin/env python3
"""
Zomato Demand Prediction MLOps Pipeline
Episode 44: MLOps at Scale

यह example Zomato का demand prediction system दिखाता है
Food delivery demand forecasting, restaurant preparation optimization,
और delivery partner allocation के लिए complete MLOps pipeline।

Production Stats:
- Zomato: 10 crore+ monthly active users
- Restaurant partners: 200,000+ across India
- Demand prediction accuracy: 85%+
- Real-time prediction latency: <100ms
- Data processing: 50+ million events daily
"""

import asyncio
import json
import logging
import pickle
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import optuna
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import warnings
warnings.filterwarnings('ignore')

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DemandPredictionFeatures:
    """Features for demand prediction model"""
    restaurant_id: str
    location_lat: float
    location_lng: float
    cuisine_type: str
    restaurant_rating: float
    avg_order_value: float
    timestamp: datetime
    
    # Time-based features
    hour_of_day: int
    day_of_week: int
    is_weekend: bool
    is_holiday: bool
    
    # Weather features
    temperature: float
    humidity: float
    weather_condition: str  # sunny, rainy, cloudy
    
    # Historical demand features
    avg_orders_last_7_days: float
    avg_orders_same_hour_last_week: float
    trend_last_30_days: float
    
    # Event features
    is_festival_season: bool
    local_event_happening: bool
    office_area: bool
    residential_area: bool
    
    # Competition features
    nearby_restaurants_count: int
    competitor_avg_rating: float
    
    # Promotional features
    discount_percentage: float
    has_offers: bool
    
    # Delivery features
    avg_delivery_time: float
    delivery_fee: float

@dataclass
class DemandPrediction:
    """Demand prediction output"""
    restaurant_id: str
    predicted_orders: int
    confidence_score: float
    prediction_timestamp: datetime
    features_used: Dict[str, float]
    model_version: str

class WeatherService:
    """Mock weather service for realistic weather data"""
    
    def __init__(self):
        self.weather_conditions = {
            "sunny": {"temp_range": (25, 40), "humidity_range": (30, 60)},
            "rainy": {"temp_range": (20, 30), "humidity_range": (70, 95)},
            "cloudy": {"temp_range": (22, 35), "humidity_range": (50, 80)}
        }
    
    def get_current_weather(self, lat: float, lng: float) -> Dict[str, Any]:
        """Get current weather for location"""
        # Simulate realistic weather patterns for Indian cities
        import random
        
        # Monsoon season simulation (June-September)
        current_month = datetime.now().month
        if 6 <= current_month <= 9:
            # Higher probability of rain during monsoon
            weather_condition = random.choices(
                ["rainy", "cloudy", "sunny"], 
                weights=[0.6, 0.3, 0.1]
            )[0]
        else:
            weather_condition = random.choices(
                ["sunny", "cloudy", "rainy"], 
                weights=[0.7, 0.2, 0.1]
            )[0]
        
        weather_data = self.weather_conditions[weather_condition]
        temperature = random.uniform(*weather_data["temp_range"])
        humidity = random.uniform(*weather_data["humidity_range"])
        
        return {
            "temperature": temperature,
            "humidity": humidity,
            "condition": weather_condition
        }

class FeatureEngineer:
    """Feature engineering for demand prediction"""
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.indian_holidays = [
            "2024-01-26", "2024-03-11", "2024-04-09", "2024-04-17", 
            "2024-05-01", "2024-05-23", "2024-07-17", "2024-08-15",
            "2024-08-19", "2024-10-02", "2024-10-12", "2024-10-31",
            "2024-11-01", "2024-11-15", "2024-12-25"
        ]
        self.festival_seasons = [
            ("2024-10-15", "2024-11-15"),  # Diwali season
            ("2024-03-01", "2024-03-15"),  # Holi season  
            ("2024-08-10", "2024-08-25"),  # Independence Day season
        ]
        
        # Indian cities with coordinates for realistic simulation
        self.indian_cities = {
            "Mumbai": {"lat": 19.0760, "lng": 72.8777},
            "Delhi": {"lat": 28.7041, "lng": 77.1025},
            "Bangalore": {"lat": 12.9716, "lng": 77.5946},
            "Hyderabad": {"lat": 17.3850, "lng": 78.4867},
            "Chennai": {"lat": 13.0827, "lng": 80.2707},
            "Kolkata": {"lat": 22.5726, "lng": 88.3639},
            "Pune": {"lat": 18.5204, "lng": 73.8567},
            "Ahmedabad": {"lat": 23.0225, "lng": 72.5714}
        }
    
    def create_features(self, 
                       restaurant_id: str, 
                       timestamp: datetime,
                       historical_data: pd.DataFrame = None) -> DemandPredictionFeatures:
        """Create comprehensive feature set for demand prediction"""
        
        # Select random city for simulation
        city = np.random.choice(list(self.indian_cities.keys()))
        city_coords = self.indian_cities[city]
        
        # Add some noise to coordinates for realistic restaurant locations
        lat = city_coords["lat"] + np.random.uniform(-0.1, 0.1)
        lng = city_coords["lng"] + np.random.uniform(-0.1, 0.1)
        
        # Get weather data
        weather = self.weather_service.get_current_weather(lat, lng)
        
        # Time-based features
        hour_of_day = timestamp.hour
        day_of_week = timestamp.weekday()
        is_weekend = day_of_week >= 5
        
        # Holiday detection
        date_str = timestamp.strftime("%Y-%m-%d")
        is_holiday = date_str in self.indian_holidays
        
        # Festival season detection
        is_festival_season = any(
            start <= date_str <= end 
            for start, end in self.festival_seasons
        )
        
        # Restaurant characteristics (simulated based on realistic patterns)
        cuisines = ["North Indian", "South Indian", "Chinese", "Italian", 
                   "Fast Food", "Biryani", "Street Food", "Continental"]
        cuisine_type = np.random.choice(cuisines)
        
        restaurant_rating = np.random.uniform(3.5, 4.8)  # Realistic rating range
        
        # Area type classification (affects demand patterns)
        office_area = np.random.choice([True, False], p=[0.3, 0.7])
        residential_area = not office_area or np.random.choice([True, False], p=[0.4, 0.6])
        
        # Historical features (simulated based on patterns)
        base_demand = self._calculate_base_demand(cuisine_type, hour_of_day, day_of_week)
        
        avg_orders_last_7_days = base_demand * np.random.uniform(0.8, 1.2)
        avg_orders_same_hour_last_week = base_demand * np.random.uniform(0.9, 1.1)
        trend_last_30_days = np.random.uniform(-0.2, 0.3)  # Growth/decline trend
        
        # Competition features
        nearby_restaurants_count = np.random.poisson(15) + 5  # 5-30 nearby restaurants
        competitor_avg_rating = np.random.uniform(3.0, 4.5)
        
        # Promotional features
        discount_percentage = np.random.choice([0, 10, 15, 20, 25], p=[0.4, 0.3, 0.15, 0.1, 0.05])
        has_offers = discount_percentage > 0
        
        # Delivery features
        avg_delivery_time = np.random.uniform(25, 45)  # 25-45 minutes
        delivery_fee = np.random.choice([0, 15, 20, 25, 30], p=[0.2, 0.3, 0.3, 0.15, 0.05])
        
        # Average order value (varies by cuisine and area)
        base_aov = {
            "North Indian": 300, "South Indian": 250, "Chinese": 350,
            "Italian": 400, "Fast Food": 200, "Biryani": 280,
            "Street Food": 150, "Continental": 450
        }
        avg_order_value = base_aov.get(cuisine_type, 300) * np.random.uniform(0.8, 1.3)
        
        return DemandPredictionFeatures(
            restaurant_id=restaurant_id,
            location_lat=lat,
            location_lng=lng,
            cuisine_type=cuisine_type,
            restaurant_rating=restaurant_rating,
            avg_order_value=avg_order_value,
            timestamp=timestamp,
            hour_of_day=hour_of_day,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            is_holiday=is_holiday,
            temperature=weather["temperature"],
            humidity=weather["humidity"],
            weather_condition=weather["condition"],
            avg_orders_last_7_days=avg_orders_last_7_days,
            avg_orders_same_hour_last_week=avg_orders_same_hour_last_week,
            trend_last_30_days=trend_last_30_days,
            is_festival_season=is_festival_season,
            local_event_happening=np.random.choice([True, False], p=[0.1, 0.9]),
            office_area=office_area,
            residential_area=residential_area,
            nearby_restaurants_count=nearby_restaurants_count,
            competitor_avg_rating=competitor_avg_rating,
            discount_percentage=discount_percentage,
            has_offers=has_offers,
            avg_delivery_time=avg_delivery_time,
            delivery_fee=delivery_fee
        )
    
    def _calculate_base_demand(self, cuisine_type: str, hour: int, day_of_week: int) -> float:
        """Calculate base demand based on cuisine, time, and day"""
        
        # Base demand by cuisine type
        cuisine_multipliers = {
            "North Indian": 1.2, "South Indian": 1.0, "Chinese": 0.9,
            "Italian": 0.7, "Fast Food": 1.3, "Biryani": 1.1,
            "Street Food": 0.8, "Continental": 0.6
        }
        
        base_demand = 50 * cuisine_multipliers.get(cuisine_type, 1.0)
        
        # Hour-based demand patterns (Indian meal times)
        hour_multipliers = {
            7: 0.3, 8: 0.5, 9: 0.7, 10: 0.4, 11: 0.6, 12: 1.2,  # Lunch buildup
            13: 1.5, 14: 1.3, 15: 0.8, 16: 0.5, 17: 0.6, 18: 0.9,  # Lunch peak
            19: 1.4, 20: 1.6, 21: 1.3, 22: 0.8, 23: 0.4  # Dinner time
        }
        
        time_multiplier = hour_multipliers.get(hour, 0.2)
        
        # Weekend boost
        weekend_multiplier = 1.3 if day_of_week >= 5 else 1.0
        
        return base_demand * time_multiplier * weekend_multiplier

class ZomatoDemandPredictor:
    """Complete MLOps pipeline for Zomato demand prediction"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.feature_engineer = FeatureEngineer()
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.model_version = "v1.0.0"
        
        # MLflow setup
        mlflow.set_tracking_uri("http://localhost:5000")  # MLflow server
        mlflow.set_experiment("zomato_demand_prediction")
        
        # Redis for caching predictions
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using in-memory caching")
            self.redis_client = None
            self.cache = {}
        
        # Model storage path
        self.model_path = Path("./models/zomato_demand_models")
        self.model_path.mkdir(parents=True, exist_ok=True)
    
    def generate_training_data(self, num_samples: int = 10000) -> pd.DataFrame:
        """Generate realistic training data for demand prediction"""
        logger.info(f"🔄 Generating {num_samples:,} training samples...")
        
        training_data = []
        
        # Generate data for 500 restaurants over past 30 days
        restaurant_ids = [f"rest_{i:04d}" for i in range(1, 501)]
        
        start_date = datetime.now() - timedelta(days=30)
        
        for _ in range(num_samples):
            restaurant_id = np.random.choice(restaurant_ids)
            
            # Random timestamp in past 30 days
            random_days = np.random.uniform(0, 30)
            timestamp = start_date + timedelta(days=random_days)
            
            # Generate features
            features = self.feature_engineer.create_features(restaurant_id, timestamp)
            
            # Calculate actual demand (target variable)
            # This simulates real-world demand based on features
            actual_demand = self._calculate_actual_demand(features)
            
            # Convert features to dictionary and add target
            feature_dict = asdict(features)
            feature_dict['actual_orders'] = actual_demand
            
            training_data.append(feature_dict)
        
        df = pd.DataFrame(training_data)
        logger.info(f"✅ Generated training data: {df.shape}")
        return df
    
    def _calculate_actual_demand(self, features: DemandPredictionFeatures) -> int:
        """Calculate realistic actual demand based on features"""
        
        # Start with base demand
        base_demand = features.avg_orders_last_7_days
        
        # Apply various multipliers based on features
        multipliers = 1.0
        
        # Time-based effects
        if features.hour_of_day in [12, 13, 19, 20, 21]:  # Peak meal times
            multipliers *= 1.4
        elif features.hour_of_day in [11, 14, 18, 22]:  # Shoulder hours
            multipliers *= 1.1
        
        # Weekend effect
        if features.is_weekend:
            multipliers *= 1.25
        
        # Holiday effect
        if features.is_holiday:
            multipliers *= 1.5
        
        # Festival season effect
        if features.is_festival_season:
            multipliers *= 1.3
        
        # Weather effects
        if features.weather_condition == "rainy":
            multipliers *= 1.6  # More orders during rain
        elif features.weather_condition == "sunny" and features.temperature > 35:
            multipliers *= 0.8  # Less orders in extreme heat
        
        # Rating effect
        if features.restaurant_rating > 4.5:
            multipliers *= 1.3
        elif features.restaurant_rating < 3.5:
            multipliers *= 0.7
        
        # Discount effect
        if features.discount_percentage > 0:
            discount_boost = 1 + (features.discount_percentage / 100)
            multipliers *= discount_boost
        
        # Delivery time penalty
        if features.avg_delivery_time > 40:
            multipliers *= 0.8
        
        # Competition effect
        if features.nearby_restaurants_count > 20:
            multipliers *= 0.9  # More competition
        
        # Area type effect
        if features.office_area and 9 <= features.hour_of_day <= 17:
            multipliers *= 1.2  # Office lunch orders
        
        # Calculate final demand
        final_demand = base_demand * multipliers
        
        # Add some noise for realism
        noise_factor = np.random.normal(1.0, 0.1)  # ±10% random variation
        final_demand = max(0, int(final_demand * noise_factor))
        
        return final_demand
    
    def preprocess_features(self, df: pd.DataFrame) -> np.ndarray:
        """Preprocess features for model training"""
        
        # Separate categorical and numerical features
        categorical_features = ['cuisine_type', 'weather_condition']
        numerical_features = [col for col in df.columns 
                            if col not in categorical_features + ['actual_orders', 'timestamp', 'restaurant_id']]
        
        processed_features = []
        
        # Handle categorical features
        for cat_feature in categorical_features:
            if cat_feature not in self.label_encoders:
                self.label_encoders[cat_feature] = LabelEncoder()
                encoded = self.label_encoders[cat_feature].fit_transform(df[cat_feature])
            else:
                encoded = self.label_encoders[cat_feature].transform(df[cat_feature])
            
            processed_features.append(encoded.reshape(-1, 1))
        
        # Handle numerical features
        numerical_data = df[numerical_features].values
        
        if 'scaler' not in self.scalers:
            self.scalers['scaler'] = StandardScaler()
            scaled_numerical = self.scalers['scaler'].fit_transform(numerical_data)
        else:
            scaled_numerical = self.scalers['scaler'].transform(numerical_data)
        
        processed_features.append(scaled_numerical)
        
        # Combine all features
        final_features = np.hstack(processed_features)
        
        return final_features
    
    def hyperparameter_tuning(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
        """Hyperparameter tuning using Optuna"""
        logger.info("🔍 Starting hyperparameter tuning...")
        
        def objective(trial):
            # Random Forest hyperparameters
            n_estimators = trial.suggest_int('n_estimators', 50, 200)
            max_depth = trial.suggest_int('max_depth', 5, 20)
            min_samples_split = trial.suggest_int('min_samples_split', 2, 20)
            min_samples_leaf = trial.suggest_int('min_samples_leaf', 1, 20)
            
            model = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                min_samples_leaf=min_samples_leaf,
                random_state=42,
                n_jobs=-1
            )
            
            # Cross-validation score
            scores = cross_val_score(model, X_train, y_train, cv=3, scoring='neg_mean_squared_error', n_jobs=-1)
            return -scores.mean()
        
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=20)  # Reduced for demo
        
        logger.info(f"✅ Best hyperparameters: {study.best_params}")
        return study.best_params
    
    def train_model(self, df: pd.DataFrame) -> Dict[str, float]:
        """Train demand prediction model with MLflow tracking"""
        
        with mlflow.start_run():
            logger.info("🚀 Starting model training...")
            
            # Preprocess features
            X = self.preprocess_features(df)
            y = df['actual_orders'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Hyperparameter tuning
            best_params = self.hyperparameter_tuning(X_train, y_train)
            
            # Train Random Forest with best parameters
            rf_model = RandomForestRegressor(**best_params, random_state=42, n_jobs=-1)
            rf_model.fit(X_train, y_train)
            
            # Train Gradient Boosting model
            gb_model = GradientBoostingRegressor(
                n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42
            )
            gb_model.fit(X_train, y_train)
            
            # Ensemble predictions
            rf_pred = rf_model.predict(X_test)
            gb_pred = gb_model.predict(X_test)
            ensemble_pred = (rf_pred + gb_pred) / 2
            
            # Calculate metrics
            mse = mean_squared_error(y_test, ensemble_pred)
            mae = mean_absolute_error(y_test, ensemble_pred)
            r2 = r2_score(y_test, ensemble_pred)
            
            metrics = {
                'mse': mse,
                'mae': mae,
                'r2_score': r2,
                'rmse': np.sqrt(mse)
            }
            
            logger.info(f"📊 Model Performance:")
            logger.info(f"  MSE: {mse:.2f}")
            logger.info(f"  MAE: {mae:.2f}")
            logger.info(f"  R²: {r2:.4f}")
            logger.info(f"  RMSE: {np.sqrt(mse):.2f}")
            
            # Log metrics to MLflow
            mlflow.log_metrics(metrics)
            mlflow.log_params(best_params)
            
            # Save models
            self.models['random_forest'] = rf_model
            self.models['gradient_boosting'] = gb_model
            
            # Save models to disk
            rf_path = self.model_path / "random_forest_model.joblib"
            gb_path = self.model_path / "gradient_boosting_model.joblib"
            scaler_path = self.model_path / "scaler.joblib"
            encoders_path = self.model_path / "encoders.joblib"
            
            joblib.dump(rf_model, rf_path)
            joblib.dump(gb_model, gb_path)
            joblib.dump(self.scalers, scaler_path)
            joblib.dump(self.label_encoders, encoders_path)
            
            # Log models to MLflow
            mlflow.sklearn.log_model(rf_model, "random_forest")
            mlflow.sklearn.log_model(gb_model, "gradient_boosting")
            
            logger.info("✅ Model training completed and saved")
            return metrics
    
    def predict_demand(self, 
                      restaurant_id: str, 
                      prediction_time: datetime = None) -> DemandPrediction:
        """Predict demand for a restaurant at given time"""
        
        if prediction_time is None:
            prediction_time = datetime.now()
        
        # Check cache first
        cache_key = f"demand_pred_{restaurant_id}_{prediction_time.hour}"
        
        if self.redis_client:
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                logger.info(f"📋 Cache hit for {restaurant_id}")
                return DemandPrediction(**json.loads(cached_result))
        elif hasattr(self, 'cache') and cache_key in self.cache:
            logger.info(f"📋 Memory cache hit for {restaurant_id}")
            return self.cache[cache_key]
        
        # Generate features
        features = self.feature_engineer.create_features(restaurant_id, prediction_time)
        
        # Convert to DataFrame for preprocessing
        feature_dict = asdict(features)
        feature_dict.pop('actual_orders', None)  # Remove if exists
        df = pd.DataFrame([feature_dict])
        
        # Preprocess features
        X = self.preprocess_features(df)
        
        # Make predictions with both models
        if 'random_forest' in self.models and 'gradient_boosting' in self.models:
            rf_pred = self.models['random_forest'].predict(X)[0]
            gb_pred = self.models['gradient_boosting'].predict(X)[0]
            
            # Ensemble prediction
            predicted_orders = int((rf_pred + gb_pred) / 2)
            
            # Calculate confidence score based on model agreement
            agreement = 1 - abs(rf_pred - gb_pred) / max(rf_pred, gb_pred, 1)
            confidence_score = min(0.95, max(0.5, agreement))
        else:
            logger.warning("Models not loaded, using baseline prediction")
            predicted_orders = int(features.avg_orders_last_7_days)
            confidence_score = 0.6
        
        # Create prediction object
        prediction = DemandPrediction(
            restaurant_id=restaurant_id,
            predicted_orders=max(0, predicted_orders),
            confidence_score=confidence_score,
            prediction_timestamp=datetime.now(),
            features_used={
                'hour_of_day': features.hour_of_day,
                'day_of_week': features.day_of_week,
                'weather_condition': features.weather_condition,
                'restaurant_rating': features.restaurant_rating,
                'discount_percentage': features.discount_percentage
            },
            model_version=self.model_version
        )
        
        # Cache the prediction
        if self.redis_client:
            self.redis_client.setex(
                cache_key, 
                300,  # 5 minutes TTL
                json.dumps(asdict(prediction), default=str)
            )
        elif hasattr(self, 'cache'):
            self.cache[cache_key] = prediction
        
        return prediction
    
    def batch_predict(self, restaurant_ids: List[str], 
                     prediction_time: datetime = None) -> List[DemandPrediction]:
        """Batch prediction for multiple restaurants"""
        logger.info(f"🔄 Batch predicting for {len(restaurant_ids)} restaurants...")
        
        predictions = []
        for restaurant_id in restaurant_ids:
            try:
                prediction = self.predict_demand(restaurant_id, prediction_time)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Error predicting for {restaurant_id}: {e}")
                continue
        
        logger.info(f"✅ Completed {len(predictions)} predictions")
        return predictions
    
    def model_monitoring(self) -> Dict[str, Any]:
        """Monitor model performance and data drift"""
        logger.info("📊 Running model monitoring checks...")
        
        # Generate recent data for monitoring
        recent_data = self.generate_training_data(1000)
        
        # Basic data quality checks
        monitoring_report = {
            "timestamp": datetime.now().isoformat(),
            "model_version": self.model_version,
            "data_quality": {
                "total_samples": len(recent_data),
                "missing_values": recent_data.isnull().sum().sum(),
                "avg_orders": recent_data['actual_orders'].mean(),
                "orders_std": recent_data['actual_orders'].std()
            },
            "feature_stats": {
                "avg_rating": recent_data['restaurant_rating'].mean(),
                "avg_delivery_time": recent_data['avg_delivery_time'].mean(),
                "discount_coverage": (recent_data['discount_percentage'] > 0).mean()
            }
        }
        
        logger.info("✅ Monitoring report generated")
        return monitoring_report

def create_demand_prediction_api():
    """Create FastAPI application for serving predictions"""
    app = FastAPI(title="Zomato Demand Prediction API", version="1.0.0")
    
    # Initialize predictor
    predictor = ZomatoDemandPredictor()
    
    class PredictionRequest(BaseModel):
        restaurant_id: str
        prediction_hour: Optional[int] = None
    
    class BatchPredictionRequest(BaseModel):
        restaurant_ids: List[str]
        prediction_hour: Optional[int] = None
    
    @app.post("/predict")
    async def predict_demand(request: PredictionRequest):
        """Single restaurant demand prediction"""
        try:
            prediction_time = datetime.now()
            if request.prediction_hour is not None:
                prediction_time = prediction_time.replace(hour=request.prediction_hour)
            
            prediction = predictor.predict_demand(request.restaurant_id, prediction_time)
            return asdict(prediction)
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/predict/batch")
    async def batch_predict_demand(request: BatchPredictionRequest):
        """Batch restaurant demand prediction"""
        try:
            prediction_time = datetime.now()
            if request.prediction_hour is not None:
                prediction_time = prediction_time.replace(hour=request.prediction_hour)
            
            predictions = predictor.batch_predict(request.restaurant_ids, prediction_time)
            return [asdict(pred) for pred in predictions]
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    @app.get("/monitoring")
    async def get_monitoring_report():
        """Get model monitoring report"""
        try:
            report = predictor.model_monitoring()
            return report
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

async def main():
    """Main demo function"""
    print("🍕 Starting Zomato Demand Prediction MLOps Pipeline")
    print("🚀 Complete ML system for food delivery demand forecasting...")
    print("📊 Training models, serving predictions, और monitoring system health...\n")
    
    # Initialize predictor
    predictor = ZomatoDemandPredictor()
    
    try:
        # Generate and train on realistic data
        print("📈 Phase 1: Data Generation and Model Training")
        training_data = predictor.generate_training_data(5000)  # Reduced for demo
        
        # Train models
        metrics = predictor.train_model(training_data)
        
        print(f"\n✅ Model Training Completed:")
        print(f"   RMSE: {metrics['rmse']:.2f} orders")
        print(f"   R² Score: {metrics['r2_score']:.4f}")
        print(f"   Mean Absolute Error: {metrics['mae']:.2f} orders")
        
        # Phase 2: Real-time predictions
        print(f"\n🔮 Phase 2: Real-time Demand Predictions")
        
        # Simulate predictions for different restaurants and times
        test_restaurants = ["rest_0001", "rest_0050", "rest_0100", "rest_0200", "rest_0300"]
        
        # Predict for current time
        current_predictions = predictor.batch_predict(test_restaurants)
        
        print(f"\n📊 Current Hour Predictions:")
        for pred in current_predictions[:5]:
            print(f"  🏪 {pred.restaurant_id}: {pred.predicted_orders} orders "
                  f"(confidence: {pred.confidence_score:.2f})")
        
        # Predict for lunch hour (13:00)
        lunch_time = datetime.now().replace(hour=13, minute=0)
        lunch_predictions = predictor.batch_predict(test_restaurants, lunch_time)
        
        print(f"\n🍽️ Lunch Hour (1 PM) Predictions:")
        for pred in lunch_predictions[:5]:
            print(f"  🏪 {pred.restaurant_id}: {pred.predicted_orders} orders "
                  f"(confidence: {pred.confidence_score:.2f})")
        
        # Predict for dinner hour (20:00)
        dinner_time = datetime.now().replace(hour=20, minute=0)
        dinner_predictions = predictor.batch_predict(test_restaurants, dinner_time)
        
        print(f"\n🌆 Dinner Hour (8 PM) Predictions:")
        for pred in dinner_predictions[:5]:
            print(f"  🏪 {pred.restaurant_id}: {pred.predicted_orders} orders "
                  f"(confidence: {pred.confidence_score:.2f})")
        
        # Phase 3: Monitoring
        print(f"\n📊 Phase 3: Model Monitoring and Health Check")
        monitoring_report = predictor.model_monitoring()
        
        print(f"📈 Model Health Report:")
        print(f"   Model Version: {monitoring_report['model_version']}")
        print(f"   Samples Monitored: {monitoring_report['data_quality']['total_samples']:,}")
        print(f"   Average Orders: {monitoring_report['data_quality']['avg_orders']:.1f}")
        print(f"   Average Rating: {monitoring_report['feature_stats']['avg_rating']:.2f}")
        print(f"   Discount Coverage: {monitoring_report['feature_stats']['discount_coverage']:.1%}")
        
        # Business insights
        print(f"\n💡 Business Insights:")
        
        # Calculate peak hours
        all_predictions = current_predictions + lunch_predictions + dinner_predictions
        avg_current = sum(p.predicted_orders for p in current_predictions) / len(current_predictions)
        avg_lunch = sum(p.predicted_orders for p in lunch_predictions) / len(lunch_predictions)
        avg_dinner = sum(p.predicted_orders for p in dinner_predictions) / len(dinner_predictions)
        
        peak_hour = "Lunch" if avg_lunch > avg_dinner else "Dinner"
        print(f"   🔥 Peak demand hour: {peak_hour}")
        print(f"   📈 Lunch vs Current: {((avg_lunch/avg_current-1)*100):+.0f}% change")
        print(f"   📈 Dinner vs Current: {((avg_dinner/avg_current-1)*100):+.0f}% change")
        
        # High demand restaurants
        high_demand = [p for p in dinner_predictions if p.predicted_orders > avg_dinner * 1.2]
        print(f"   🌟 High-demand restaurants (dinner): {len(high_demand)}")
        
    except Exception as e:
        logger.error(f"❌ Error in demo: {e}")
        raise
    
    finally:
        print(f"\n🎯 DEMO COMPLETED!")
        print(f"💡 In production, this system would:")
        print(f"   - Process 50M+ events daily from Zomato app")
        print(f"   - Serve 10,000+ predictions per second")
        print(f"   - Update models automatically with new data")
        print(f"   - Optimize restaurant preparation और delivery allocation")
        print(f"   - Handle festival rush और weather-based demand spikes")

if __name__ == "__main__":
    # Run the complete demo
    asyncio.run(main())
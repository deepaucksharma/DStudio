#!/usr/bin/env python3
"""
MLflow Experiment Tracking for Indian Food Delivery
भारतीय फूड डिलीवरी के लिए एमएलफ्लो एक्सपेरिमेंट ट्रैकिंग

Comprehensive experiment tracking system for ML models
Zomato, Swiggy, Dunzo जैसे platforms के लिए optimized

Author: System Design Hindi Podcast
Cost: ~₹15,000/month for tracking infrastructure
"""

import mlflow
import mlflow.sklearn
import mlflow.xgboost
import mlflow.pytorch
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as xgb
import logging
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FoodDeliveryMLTracker:
    """
    Food delivery के लिए specialized ML experiment tracker
    Indian markets के specific requirements को handle करता है
    """
    
    def __init__(self, 
                 tracking_uri: str = "http://localhost:5000",
                 experiment_name: str = "food-delivery-demand-prediction"):
        """
        Initialize MLflow tracking for food delivery experiments
        
        Args:
            tracking_uri: MLflow server URI
            experiment_name: Name of the experiment
        """
        mlflow.set_tracking_uri(tracking_uri)
        
        # Set or create experiment
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(
                    experiment_name,
                    tags={
                        "project": "indian-food-delivery",
                        "team": "data-science",
                        "region": "mumbai-delhi-bangalore",
                        "created_by": "system-design-hindi"
                    }
                )
            else:
                experiment_id = experiment.experiment_id
                
            mlflow.set_experiment(experiment_name)
            self.experiment_name = experiment_name
            logger.info(f"Experiment '{experiment_name}' initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize experiment: {str(e)}")
            raise
    
    def log_indian_context_params(self, 
                                  city: str = "mumbai",
                                  season: str = "monsoon",
                                  festival_period: bool = False,
                                  delivery_radius_km: float = 5.0):
        """
        Indian context के specific parameters log करता है
        Mumbai monsoon, Delhi winter, Bangalore traffic का consideration
        """
        context_params = {
            "city": city,
            "season": season,
            "festival_period": festival_period,
            "delivery_radius_km": delivery_radius_km,
            "indian_context_enabled": True
        }
        
        # City-specific parameters
        city_configs = {
            "mumbai": {
                "monsoon_impact": True,
                "local_train_dependency": True,
                "peak_hours": "12-14,19-22",
                "avg_delivery_time_min": 35,
                "traffic_multiplier": 1.8
            },
            "delhi": {
                "pollution_impact": True,
                "metro_dependency": True,
                "peak_hours": "12-14,20-22",
                "avg_delivery_time_min": 30,
                "traffic_multiplier": 1.6
            },
            "bangalore": {
                "traffic_congestion": True,
                "it_crowd_dependency": True,
                "peak_hours": "12-14,19-21",
                "avg_delivery_time_min": 40,
                "traffic_multiplier": 2.0
            }
        }
        
        if city in city_configs:
            context_params.update(city_configs[city])
        
        mlflow.log_params(context_params)
        logger.info(f"Indian context parameters logged for {city}")
    
    def track_zomato_experiment(self, 
                               model_type: str = "xgboost",
                               hyperparams: Dict[str, Any] = None,
                               training_data_path: str = None):
        """
        Zomato-style demand prediction experiment tracking
        Restaurant recommendations और delivery time prediction के लिए
        """
        with mlflow.start_run(run_name=f"zomato_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M')}"):
            
            # Log Indian context
            self.log_indian_context_params(
                city="mumbai",
                season="post_monsoon",
                festival_period=False,
                delivery_radius_km=4.5
            )
            
            # Generate sample Zomato data
            np.random.seed(42)
            n_samples = 10000
            
            # Features: Zomato specific
            data = {
                'restaurant_rating': np.random.uniform(1.0, 5.0, n_samples),
                'cuisine_popularity': np.random.uniform(0.1, 1.0, n_samples),
                'delivery_distance_km': np.random.exponential(2.0, n_samples),
                'peak_hour': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
                'rain_intensity': np.random.exponential(0.5, n_samples),
                'restaurant_busy_score': np.random.uniform(0.0, 1.0, n_samples),
                'customer_loyalty_score': np.random.uniform(0.0, 1.0, n_samples),
                'area_affluence_index': np.random.uniform(0.2, 1.0, n_samples),
                'festival_boost': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
                'discount_percentage': np.random.uniform(0.0, 50.0, n_samples)
            }
            
            df = pd.DataFrame(data)
            
            # Target: delivery_demand_score (0-100)
            df['delivery_demand_score'] = (
                30 * df['restaurant_rating'] / 5.0 +
                20 * df['cuisine_popularity'] +
                15 * (1 / (1 + df['delivery_distance_km'])) +
                10 * df['peak_hour'] +
                5 * (1 - df['rain_intensity'] / 5.0).clip(0, 1) +
                10 * df['restaurant_busy_score'] +
                5 * df['customer_loyalty_score'] +
                5 * df['area_affluence_index'] +
                10 * df['festival_boost'] +
                2 * df['discount_percentage'] / 50.0 +
                np.random.normal(0, 5, n_samples)
            ).clip(0, 100)
            
            # Log dataset info
            mlflow.log_param("dataset_size", len(df))
            mlflow.log_param("feature_count", len(df.columns) - 1)
            mlflow.log_param("target_variable", "delivery_demand_score")
            
            # Split data
            X = df.drop('delivery_demand_score', axis=1)
            y = df['delivery_demand_score']
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model based on type
            if model_type == "xgboost":
                model = self._train_xgboost_zomato(X_train, y_train, hyperparams)
            elif model_type == "random_forest":
                model = self._train_random_forest_zomato(X_train, y_train, hyperparams)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Indian market specific metrics
            peak_hour_mask = X_test['peak_hour'] == 1
            peak_hour_mae = mean_absolute_error(y_test[peak_hour_mask], y_pred[peak_hour_mask])
            
            rain_mask = X_test['rain_intensity'] > 1.0
            rain_mae = mean_absolute_error(y_test[rain_mask], y_pred[rain_mask]) if rain_mask.sum() > 0 else 0
            
            # Log metrics
            metrics = {
                "mse": mse,
                "rmse": rmse,
                "mae": mae,
                "r2_score": r2,
                "peak_hour_mae": peak_hour_mae,
                "rain_condition_mae": rain_mae,
                "model_accuracy_percentage": max(0, (1 - mae / 100) * 100)
            }
            
            mlflow.log_metrics(metrics)
            
            # Log model
            if model_type == "xgboost":
                mlflow.xgboost.log_model(model, "model")
            else:
                mlflow.sklearn.log_model(model, "model")
            
            # Feature importance analysis
            if hasattr(model, 'feature_importances_'):
                feature_importance = dict(zip(X.columns, model.feature_importances_))
                
                # Log top features as parameters
                sorted_features = sorted(feature_importance.items(), 
                                       key=lambda x: x[1], reverse=True)[:5]
                for i, (feature, importance) in enumerate(sorted_features):
                    mlflow.log_param(f"top_feature_{i+1}", f"{feature}:{importance:.4f}")
                
                # Create and log feature importance plot
                plt.figure(figsize=(10, 6))
                features = list(feature_importance.keys())
                importances = list(feature_importance.values())
                
                plt.barh(features, importances)
                plt.title('Zomato Demand Prediction - Feature Importance')
                plt.xlabel('Importance Score')
                plt.tight_layout()
                
                importance_plot_path = "feature_importance_zomato.png"
                plt.savefig(importance_plot_path)
                mlflow.log_artifact(importance_plot_path)
                plt.close()
            
            # Business impact metrics (Indian market context)
            business_metrics = self._calculate_business_impact(
                y_test, y_pred, X_test, model_type="zomato"
            )
            mlflow.log_metrics(business_metrics)
            
            # Log cost analysis
            cost_analysis = {
                "infrastructure_cost_inr_monthly": 25000,
                "ml_engineer_cost_inr_monthly": 150000,
                "data_storage_cost_inr_monthly": 5000,
                "total_ml_cost_inr_monthly": 180000,
                "revenue_impact_inr_monthly": 500000,  # Estimated revenue increase
                "roi_percentage": ((500000 - 180000) / 180000) * 100
            }
            mlflow.log_params(cost_analysis)
            
            logger.info(f"Zomato experiment completed - R² Score: {r2:.4f}")
            return mlflow.active_run().info.run_id
    
    def track_swiggy_experiment(self, 
                               delivery_optimization: bool = True,
                               hyperparams: Dict[str, Any] = None):
        """
        Swiggy-style delivery time optimization experiment
        Real-time delivery route optimization और demand surge prediction
        """
        with mlflow.start_run(run_name=f"swiggy_delivery_opt_{datetime.now().strftime('%Y%m%d_%H%M')}"):
            
            # Log Swiggy context
            self.log_indian_context_params(
                city="bangalore",
                season="summer",
                festival_period=False,
                delivery_radius_km=6.0
            )
            
            # Swiggy specific parameters
            swiggy_params = {
                "delivery_optimization_enabled": delivery_optimization,
                "surge_pricing_enabled": True,
                "multi_restaurant_orders": True,
                "delivery_partner_pooling": True,
                "real_time_traffic_integration": True
            }
            mlflow.log_params(swiggy_params)
            
            # Generate Swiggy delivery data
            np.random.seed(123)
            n_orders = 15000
            
            delivery_data = {
                'order_value_inr': np.random.lognormal(4.5, 0.8, n_orders),
                'delivery_distance_km': np.random.exponential(3.0, n_orders),
                'traffic_density': np.random.uniform(0.1, 1.0, n_orders),
                'delivery_partner_rating': np.random.uniform(3.0, 5.0, n_orders),
                'restaurant_prep_time_min': np.random.exponential(15, n_orders),
                'customer_tier': np.random.choice([1, 2, 3], n_orders, p=[0.6, 0.3, 0.1]),
                'weather_score': np.random.uniform(0.3, 1.0, n_orders),
                'area_delivery_density': np.random.uniform(0.2, 1.0, n_orders),
                'surge_multiplier': np.random.choice([1.0, 1.2, 1.5, 2.0], n_orders, p=[0.7, 0.15, 0.1, 0.05]),
                'time_of_day_score': np.random.uniform(0.1, 1.0, n_orders)
            }
            
            delivery_df = pd.DataFrame(delivery_data)
            
            # Target: delivery_time_minutes
            delivery_df['delivery_time_minutes'] = (
                15 +  # Base time
                2 * delivery_df['delivery_distance_km'] +
                10 * delivery_df['traffic_density'] +
                0.3 * delivery_df['restaurant_prep_time_min'] +
                5 * (1 - delivery_df['weather_score']) +
                -2 * (delivery_df['delivery_partner_rating'] - 3) +
                3 * (1 / delivery_df['area_delivery_density']) +
                np.random.normal(0, 3, n_orders)
            ).clip(10, 90)
            
            # Train delivery time prediction model
            X = delivery_df.drop('delivery_time_minutes', axis=1)
            y = delivery_df['delivery_time_minutes']
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # XGBoost for delivery time prediction
            model = xgb.XGBRegressor(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Metrics
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Swiggy specific metrics
            surge_mask = X_test['surge_multiplier'] > 1.0
            surge_accuracy = mean_absolute_error(y_test[surge_mask], y_pred[surge_mask])
            
            premium_mask = X_test['customer_tier'] == 3
            premium_accuracy = mean_absolute_error(y_test[premium_mask], y_pred[premium_mask])
            
            delivery_metrics = {
                "delivery_time_mse": mse,
                "delivery_time_mae": mae,
                "delivery_time_r2": r2,
                "surge_condition_mae": surge_accuracy,
                "premium_customer_mae": premium_accuracy,
                "on_time_delivery_rate": np.mean(np.abs(y_pred - y_test) <= 5) * 100  # Within 5 min
            }
            
            mlflow.log_metrics(delivery_metrics)
            mlflow.xgboost.log_model(model, "delivery_time_model")
            
            # Business impact for Swiggy
            business_impact = {
                "delivery_cost_reduction_percentage": 12,
                "customer_satisfaction_improvement": 8.5,
                "delivery_partner_efficiency_gain": 15,
                "order_fulfillment_improvement": 10,
                "cost_savings_inr_monthly": 400000,
                "revenue_increase_inr_monthly": 600000
            }
            mlflow.log_metrics(business_impact)
            
            logger.info(f"Swiggy delivery optimization experiment completed")
            return mlflow.active_run().info.run_id
    
    def _train_xgboost_zomato(self, X_train, y_train, hyperparams=None):
        """XGBoost model for Zomato demand prediction"""
        default_params = {
            'n_estimators': 300,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8
        }
        
        if hyperparams:
            default_params.update(hyperparams)
        
        mlflow.log_params(default_params)
        
        model = xgb.XGBRegressor(**default_params, random_state=42)
        model.fit(X_train, y_train)
        
        return model
    
    def _train_random_forest_zomato(self, X_train, y_train, hyperparams=None):
        """Random Forest model for Zomato demand prediction"""
        default_params = {
            'n_estimators': 200,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2
        }
        
        if hyperparams:
            default_params.update(hyperparams)
            
        mlflow.log_params(default_params)
        
        model = RandomForestRegressor(**default_params, random_state=42)
        model.fit(X_train, y_train)
        
        return model
    
    def _calculate_business_impact(self, y_true, y_pred, X_test, model_type="zomato"):
        """Calculate business impact metrics for Indian food delivery"""
        
        mae = mean_absolute_error(y_true, y_pred)
        
        if model_type == "zomato":
            # Zomato business metrics
            accurate_predictions = np.abs(y_true - y_pred) <= 10  # Within 10 points
            accuracy_rate = np.mean(accurate_predictions) * 100
            
            # Revenue impact calculation
            avg_order_value = 350  # INR
            orders_per_day = 50000  # Mumbai
            
            # Better predictions = higher conversion
            conversion_improvement = accuracy_rate * 0.001  # 0.1% per accuracy point
            revenue_increase_daily = orders_per_day * avg_order_value * (conversion_improvement / 100)
            
            return {
                "prediction_accuracy_rate": accuracy_rate,
                "revenue_increase_inr_daily": revenue_increase_daily,
                "revenue_increase_inr_monthly": revenue_increase_daily * 30,
                "customer_satisfaction_score": min(95, 60 + accuracy_rate * 0.4),
                "restaurant_partner_retention": min(95, 70 + accuracy_rate * 0.3)
            }
        
        return {}
    
    def compare_experiments(self, experiment_names: List[str] = None):
        """
        Multiple experiments को compare करता है
        Best performing model का selection करने के लिए
        """
        if experiment_names is None:
            experiment_names = [self.experiment_name]
        
        comparison_data = []
        
        for exp_name in experiment_names:
            experiment = mlflow.get_experiment_by_name(exp_name)
            if experiment:
                runs = mlflow.search_runs(
                    experiment_ids=[experiment.experiment_id],
                    order_by=["metrics.r2_score DESC"],
                    max_results=10
                )
                
                for _, run in runs.iterrows():
                    comparison_data.append({
                        'experiment': exp_name,
                        'run_id': run['run_id'],
                        'r2_score': run.get('metrics.r2_score', 0),
                        'mae': run.get('metrics.mae', float('inf')),
                        'model_type': run.get('params.model_type', 'unknown'),
                        'city': run.get('params.city', 'unknown'),
                        'accuracy_rate': run.get('metrics.prediction_accuracy_rate', 0)
                    })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        if not comparison_df.empty:
            # Best models by different criteria
            best_overall = comparison_df.loc[comparison_df['r2_score'].idxmax()]
            best_accuracy = comparison_df.loc[comparison_df['accuracy_rate'].idxmax()]
            
            print("🏆 Best Models Summary:")
            print(f"Best R² Score: {best_overall['r2_score']:.4f} (Run: {best_overall['run_id'][:8]})")
            print(f"Best Accuracy: {best_accuracy['accuracy_rate']:.2f}% (Run: {best_accuracy['run_id'][:8]})")
            
            return comparison_df
        
        return pd.DataFrame()
    
    def generate_model_registry_report(self):
        """
        Model registry के लिए comprehensive report generate करता है
        Production deployment decisions के लिए
        """
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        runs = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["metrics.r2_score DESC"],
            max_results=5
        )
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "experiment_name": self.experiment_name,
            "total_runs": len(runs),
            "best_models": [],
            "production_recommendations": []
        }
        
        for _, run in runs.head(3).iterrows():
            model_info = {
                "run_id": run['run_id'],
                "r2_score": run.get('metrics.r2_score', 0),
                "mae": run.get('metrics.mae', 0),
                "model_type": run.get('params.model_type', 'unknown'),
                "city": run.get('params.city', 'unknown'),
                "business_impact": {
                    "revenue_increase_monthly": run.get('metrics.revenue_increase_inr_monthly', 0),
                    "accuracy_rate": run.get('metrics.prediction_accuracy_rate', 0)
                }
            }
            report["best_models"].append(model_info)
        
        # Production recommendations
        if len(runs) > 0:
            best_run = runs.iloc[0]
            r2_score = best_run.get('metrics.r2_score', 0)
            
            if r2_score > 0.8:
                report["production_recommendations"].append("✅ Ready for production deployment")
            elif r2_score > 0.7:
                report["production_recommendations"].append("⚠️ Acceptable for staging deployment")
            else:
                report["production_recommendations"].append("❌ Needs improvement before deployment")
        
        return report

# Usage Example and Demo
def run_food_delivery_experiments():
    """
    Complete food delivery ML experiments का demo
    Zomato और Swiggy दोनों के लिए models train करके compare करते हैं
    """
    print("🚀 Starting Food Delivery ML Experiments")
    print("=" * 50)
    
    # Initialize tracker
    tracker = FoodDeliveryMLTracker(
        tracking_uri="sqlite:///food_delivery_mlruns.db",
        experiment_name="indian-food-delivery-optimization"
    )
    
    # Zomato experiments
    print("\n📊 Running Zomato Experiments...")
    zomato_run_1 = tracker.track_zomato_experiment(
        model_type="xgboost",
        hyperparams={"n_estimators": 200, "max_depth": 5}
    )
    
    zomato_run_2 = tracker.track_zomato_experiment(
        model_type="random_forest",
        hyperparams={"n_estimators": 150, "max_depth": 8}
    )
    
    # Swiggy experiments
    print("\n🚚 Running Swiggy Delivery Optimization...")
    swiggy_run = tracker.track_swiggy_experiment(
        delivery_optimization=True,
        hyperparams={"n_estimators": 250, "max_depth": 6}
    )
    
    # Compare experiments
    print("\n📈 Comparing Experiments...")
    comparison = tracker.compare_experiments()
    print(comparison.head())
    
    # Generate registry report
    print("\n📋 Generating Model Registry Report...")
    registry_report = tracker.generate_model_registry_report()
    
    print("\n✨ Experiment Summary:")
    print(f"Total experiments: {len(comparison)}")
    print(f"Best R² Score: {comparison['r2_score'].max():.4f}")
    print(f"Best Accuracy: {comparison['accuracy_rate'].max():.2f}%")
    
    # Save report
    with open("model_registry_report.json", "w") as f:
        json.dump(registry_report, f, indent=2)
    
    print("\n💰 Cost Analysis:")
    print("MLflow Infrastructure: ₹15,000/month")
    print("Compute Resources: ₹25,000/month")
    print("Expected ROI: 200-300%")
    
    return tracker, comparison, registry_report

if __name__ == "__main__":
    tracker, comparison, report = run_food_delivery_experiments()
    print("\n🎉 Food Delivery ML Tracking Complete!")
    print("📊 View experiments at: http://localhost:5000")
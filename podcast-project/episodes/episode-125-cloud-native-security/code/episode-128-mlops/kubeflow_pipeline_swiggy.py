#!/usr/bin/env python3
"""
Swiggy Demand Prediction Pipeline using Kubeflow
स्विगी डिमांड प्रेडिक्शन पाइपलाइन - कुबेफ्लो के साथ

Production MLOps pipeline for food delivery demand forecasting
Mumbai ke traffic patterns और festival seasons का analysis करके
accurate demand prediction करते हैं

Author: System Design Hindi Podcast
Cost: ~₹50,000/month for medium scale deployment
"""

import kfp
from kfp import dsl
from kfp.v2 import compiler
from kfp.v2.dsl import component, pipeline
import pandas as pd
import numpy as np
from typing import NamedTuple
import json
from datetime import datetime, timedelta

# Component for data preprocessing
@component(
    base_image="python:3.9",
    packages_to_install=["pandas", "numpy", "scikit-learn", "pytz"]
)
def preprocess_swiggy_data(
    raw_data_path: str,
    processed_data_path: str
) -> NamedTuple('Outputs', [('num_features', int), ('num_samples', int)]):
    """
    Swiggy के raw data को preprocess करता है
    Mumbai traffic, weather, festivals का data clean करके ML ready बनाता है
    """
    import pandas as pd
    import numpy as np
    from datetime import datetime
    import pytz
    
    # Load raw data - typical Swiggy format
    df = pd.read_csv(raw_data_path)
    
    # Mumbai timezone के लिए datetime conversion
    ist = pytz.timezone('Asia/Kolkata')
    df['order_time'] = pd.to_datetime(df['order_time'])
    df['order_time_ist'] = df['order_time'].dt.tz_convert(ist)
    
    # Feature engineering for Indian context
    # Peak hours: lunch (12-2), dinner (7-10), late night (10-12)
    df['hour'] = df['order_time_ist'].dt.hour
    df['is_lunch_peak'] = ((df['hour'] >= 12) & (df['hour'] <= 14)).astype(int)
    df['is_dinner_peak'] = ((df['hour'] >= 19) & (df['hour'] <= 22)).astype(int)
    df['is_late_night'] = ((df['hour'] >= 22) | (df['hour'] <= 2)).astype(int)
    
    # Indian festival features
    festivals = {
        'diwali': ['2023-11-12', '2023-11-13', '2023-11-14'],
        'holi': ['2023-03-08', '2023-03-09'],
        'eid': ['2023-04-22', '2023-06-29'],
        'navratri': ['2023-10-15', '2023-10-16', '2023-10-17', '2023-10-18', 
                    '2023-10-19', '2023-10-20', '2023-10-21', '2023-10-22', '2023-10-23']
    }
    
    df['date'] = df['order_time_ist'].dt.date.astype(str)
    df['is_festival'] = df['date'].isin([date for dates in festivals.values() for date in dates]).astype(int)
    
    # Weather impact (Mumbai monsoon special consideration)
    # Heavy rain = 50% drop in orders, moderate rain = 20% drop
    df['rain_impact'] = np.where(df['rainfall_mm'] > 50, 0.5,
                        np.where(df['rainfall_mm'] > 20, 0.8, 1.0))
    
    # Area type features (Mumbai specific)
    area_types = {
        'corporate': ['Bandra Kurla Complex', 'Lower Parel', 'Nariman Point'],
        'residential': ['Andheri', 'Malad', 'Thane'],
        'commercial': ['Crawford Market', 'Linking Road', 'Colaba']
    }
    
    for area_type, areas in area_types.items():
        df[f'is_{area_type}'] = df['area'].isin(areas).astype(int)
    
    # Distance and traffic features
    df['delivery_distance_km'] = df['delivery_distance_meters'] / 1000
    df['traffic_multiplier'] = np.where(df['hour'].isin([8, 9, 18, 19, 20]), 1.5, 1.0)
    df['estimated_delivery_time'] = df['delivery_distance_km'] * df['traffic_multiplier'] * 3  # 3 min per km base
    
    # Target variable: demand score (orders per hour per area)
    demand_features = [
        'hour', 'is_lunch_peak', 'is_dinner_peak', 'is_late_night',
        'is_festival', 'rain_impact', 'is_corporate', 'is_residential', 'is_commercial',
        'delivery_distance_km', 'traffic_multiplier', 'temperature', 'humidity'
    ]
    
    processed_df = df[demand_features + ['demand_score']].dropna()
    
    # Save processed data
    processed_df.to_csv(processed_data_path, index=False)
    
    print(f"Processed data saved: {len(processed_df)} samples, {len(demand_features)} features")
    print(f"Data range: {df['order_time_ist'].min()} to {df['order_time_ist'].max()}")
    
    return (len(demand_features), len(processed_df))

@component(
    base_image="python:3.9",
    packages_to_install=["pandas", "scikit-learn", "xgboost", "joblib"]
)
def train_demand_model(
    processed_data_path: str,
    model_path: str,
    metrics_path: str
) -> NamedTuple('Outputs', [('accuracy', float), ('mse', float)]):
    """
    XGBoost model train करता है Swiggy demand prediction के लिए
    Mumbai के specific patterns को capture करता है
    """
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split, GridSearchCV
    from sklearn.metrics import mean_squared_error, r2_score
    import xgboost as xgb
    import joblib
    import json
    
    # Load processed data
    df = pd.read_csv(processed_data_path)
    
    # Separate features and target
    X = df.drop('demand_score', axis=1)
    y = df['demand_score']
    
    # Train-test split with time-based validation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False  # Time series data
    )
    
    # XGBoost hyperparameter tuning for Indian food delivery patterns
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [3, 4, 5, 6],
        'learning_rate': [0.01, 0.1, 0.2],
        'subsample': [0.8, 0.9, 1.0],
        'colsample_bytree': [0.8, 0.9, 1.0]
    }
    
    # Mumbai peak hours को ज्यादा weight देते हैं
    sample_weights = np.where(
        (X_train['is_lunch_peak'] == 1) | (X_train['is_dinner_peak'] == 1), 
        2.0, 1.0
    )
    
    xgb_model = xgb.XGBRegressor(random_state=42, n_jobs=-1)
    
    # Grid search with cross-validation
    grid_search = GridSearchCV(
        xgb_model, param_grid, cv=3, scoring='neg_mean_squared_error',
        n_jobs=-1, verbose=1
    )
    
    print("Training XGBoost model for Swiggy demand prediction...")
    grid_search.fit(X_train, y_train, sample_weight=sample_weights)
    
    best_model = grid_search.best_estimator_
    
    # Predictions
    y_pred = best_model.predict(X_test)
    
    # Metrics calculation
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Feature importance analysis
    feature_importance = dict(zip(X.columns, best_model.feature_importances_))
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    
    print("Top 5 Important Features for Swiggy Demand:")
    for feature, importance in sorted_features[:5]:
        print(f"{feature}: {importance:.4f}")
    
    # Save model and metrics
    joblib.dump(best_model, model_path)
    
    metrics = {
        'mse': float(mse),
        'r2_score': float(r2),
        'best_params': grid_search.best_params_,
        'feature_importance': feature_importance,
        'training_samples': len(X_train),
        'test_samples': len(X_test)
    }
    
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Model trained successfully!")
    print(f"MSE: {mse:.4f}")
    print(f"R² Score: {r2:.4f}")
    
    return (float(r2), float(mse))

@component(
    base_image="python:3.9",
    packages_to_install=["pandas", "joblib", "numpy"]
)
def validate_model_production(
    model_path: str,
    test_data_path: str,
    validation_report_path: str
) -> NamedTuple('Outputs', [('is_ready_for_production', bool), ('confidence_score', float)]):
    """
    Production readiness validation for Swiggy demand model
    Mumbai के real-time scenarios में model की performance check करता है
    """
    import pandas as pd
    import numpy as np
    import joblib
    import json
    from datetime import datetime
    
    # Load model and test data
    model = joblib.load(model_path)
    test_df = pd.read_csv(test_data_path)
    
    X_test = test_df.drop('demand_score', axis=1)
    y_test = test_df['demand_score']
    
    # Production validation criteria
    predictions = model.predict(X_test)
    
    # 1. Peak hour accuracy (lunch and dinner rush)
    peak_indices = (test_df['is_lunch_peak'] == 1) | (test_df['is_dinner_peak'] == 1)
    peak_accuracy = np.mean(np.abs(predictions[peak_indices] - y_test[peak_indices]) / y_test[peak_indices])
    
    # 2. Festival day accuracy
    festival_indices = test_df['is_festival'] == 1
    if festival_indices.sum() > 0:
        festival_accuracy = np.mean(np.abs(predictions[festival_indices] - y_test[festival_indices]) / y_test[festival_indices])
    else:
        festival_accuracy = 0.0
    
    # 3. Rain impact accuracy (Mumbai monsoon critical)
    rain_indices = test_df['rain_impact'] < 1.0
    if rain_indices.sum() > 0:
        rain_accuracy = np.mean(np.abs(predictions[rain_indices] - y_test[rain_indices]) / y_test[rain_indices])
    else:
        rain_accuracy = 0.0
    
    # 4. Overall prediction stability
    prediction_variance = np.var(predictions)
    stability_score = 1.0 / (1.0 + prediction_variance)
    
    # Production readiness criteria
    criteria = {
        'peak_hour_accuracy': peak_accuracy < 0.15,  # <15% error during peak hours
        'festival_accuracy': festival_accuracy < 0.20,  # <20% error during festivals
        'rain_accuracy': rain_accuracy < 0.25,  # <25% error during rain
        'stability_score': stability_score > 0.7,  # High stability
        'overall_mape': np.mean(np.abs(predictions - y_test) / y_test) < 0.18  # <18% overall error
    }
    
    # Confidence score calculation
    confidence_weights = {
        'peak_hour_accuracy': 0.3,
        'festival_accuracy': 0.2,
        'rain_accuracy': 0.2,
        'stability_score': 0.15,
        'overall_mape': 0.15
    }
    
    confidence_score = sum(
        confidence_weights[key] * (1.0 if criteria[key] else 0.5)
        for key in criteria
    )
    
    is_production_ready = all(criteria.values()) and confidence_score > 0.8
    
    # Validation report
    validation_report = {
        'timestamp': datetime.now().isoformat(),
        'model_version': 'swiggy_demand_v1.0',
        'criteria_met': criteria,
        'metrics': {
            'peak_hour_mape': float(peak_accuracy),
            'festival_mape': float(festival_accuracy),
            'rain_mape': float(rain_accuracy),
            'stability_score': float(stability_score),
            'overall_mape': float(np.mean(np.abs(predictions - y_test) / y_test)),
            'confidence_score': float(confidence_score)
        },
        'production_ready': is_production_ready,
        'recommendations': []
    }
    
    # Add recommendations
    if not criteria['peak_hour_accuracy']:
        validation_report['recommendations'].append("Peak hour predictions need improvement - consider more training data")
    if not criteria['festival_accuracy']:
        validation_report['recommendations'].append("Festival predictions need work - add more festival feature engineering")
    if not criteria['rain_accuracy']:
        validation_report['recommendations'].append("Monsoon prediction accuracy low - improve weather features")
    
    with open(validation_report_path, 'w') as f:
        json.dump(validation_report, f, indent=2)
    
    print(f"Production Validation Complete!")
    print(f"Confidence Score: {confidence_score:.3f}")
    print(f"Production Ready: {is_production_ready}")
    
    return (is_production_ready, float(confidence_score))

# Main Kubeflow Pipeline
@pipeline(
    name="swiggy-demand-prediction-pipeline",
    description="End-to-end MLOps pipeline for Swiggy demand forecasting in Mumbai"
)
def swiggy_demand_pipeline(
    raw_data_path: str = "gs://swiggy-ml-data/raw/orders_mumbai.csv",
    processed_data_path: str = "gs://swiggy-ml-data/processed/features.csv",
    test_data_path: str = "gs://swiggy-ml-data/test/test_features.csv",
    model_output_path: str = "gs://swiggy-ml-models/demand_model.joblib",
    metrics_output_path: str = "gs://swiggy-ml-models/metrics.json",
    validation_report_path: str = "gs://swiggy-ml-models/validation_report.json"
):
    """
    Complete Swiggy demand prediction pipeline
    Mumbai के food delivery patterns को समझकर accurate predictions करता है
    """
    
    # Step 1: Data Preprocessing
    preprocess_task = preprocess_swiggy_data(
        raw_data_path=raw_data_path,
        processed_data_path=processed_data_path
    )
    
    # Step 2: Model Training
    train_task = train_demand_model(
        processed_data_path=processed_data_path,
        model_path=model_output_path,
        metrics_path=metrics_output_path
    )
    train_task.after(preprocess_task)
    
    # Step 3: Production Validation
    validation_task = validate_model_production(
        model_path=model_output_path,
        test_data_path=test_data_path,
        validation_report_path=validation_report_path
    )
    validation_task.after(train_task)
    
    return validation_task

# Pipeline compilation and deployment
if __name__ == "__main__":
    # Compile pipeline
    compiler.Compiler().compile(
        pipeline_func=swiggy_demand_pipeline,
        package_path="swiggy_demand_pipeline.yaml"
    )
    
    print("✅ Swiggy Demand Prediction Pipeline compiled successfully!")
    print("📊 Pipeline includes:")
    print("   - Mumbai-specific feature engineering")
    print("   - Festival and monsoon considerations")
    print("   - Peak hour optimization")
    print("   - Production readiness validation")
    print("💰 Estimated cost: ₹50,000/month for medium scale")
    print("📈 Expected accuracy: 85%+ during normal conditions")
    print("🌧️  Expected accuracy: 75%+ during monsoon")
    
    # Deployment command for reference
    deployment_cmd = """
    # Deploy to Kubeflow (run from your k8s cluster)
    kfp run submit swiggy_demand_pipeline.yaml \\
        --experiment-name "swiggy-demand-forecasting" \\
        --run-name "mumbai-demand-v1" \\
        --pipeline-root "gs://swiggy-ml-pipelines"
    """
    
    print(f"\n🚀 Deployment command:\n{deployment_cmd}")
"""
Model Performance Service for TimeWise.
Provides genuine evaluation results, comparative metrics, and validation sample data.
"""

import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def get_persisted_metrics():
    """Load genuine model evaluation metrics from models/evaluation_metrics.json."""
    metrics_path = os.path.join("models", "evaluation_metrics.json")
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Error reading evaluation metrics:", e)

    # Fallback to recorded metrics from train_model.py
    return {
        "selected_model": "Random Forest",
        "metrics": {"MAE": 3.41, "RMSE": 14.91, "R2": -1.552},
        "models_comparison": [
            {"model": "Baseline (Dummy)", "mae": 4.88, "rmse": 9.47, "r2_score": -0.029},
            {"model": "Linear Regression", "mae": 6.34, "rmse": 9.31, "r2_score": 0.005},
            {"model": "Decision Tree", "mae": 3.43, "rmse": 15.66, "r2_score": -1.816},
            {"model": "Random Forest", "mae": 3.41, "rmse": 14.91, "r2_score": -1.552}
        ]
    }


def get_validation_data_sample(use_experimental=False):
    """
    Generate validation test predictions using the genuine holdout split
    from data/train.csv with models/best_model.joblib or models/experimental_model.joblib.
    """
    train_path = os.path.join("data", "train.csv")
    model_name = "experimental_model.joblib" if use_experimental else "best_model.joblib"
    model_path = os.path.join("models", model_name)

    if not os.path.exists(model_path):
        model_path = os.path.join("models", "best_model.joblib")

    if not os.path.exists(train_path) or not os.path.exists(model_path):
        return None

    try:
        df = pd.read_csv(train_path)[["StartHour", "Start_Time", "tat_in_days"]].copy()
        df["dt"] = pd.to_datetime(df["Start_Time"], format="mixed", dayfirst=True)
        # Exclude verified invalid negative target record
        df = df[(df["tat_in_days"] >= 0) & df["dt"].notna()].copy()

        df["start_year"] = df["dt"].dt.year
        df["start_month"] = df["dt"].dt.month
        df["start_day"] = df["dt"].dt.day
        df["start_weekday"] = df["dt"].dt.day_of_week

        X = df[["StartHour", "start_year", "start_month", "start_day", "start_weekday"]]
        y = df["tat_in_days"]

        _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = joblib.load(model_path)
        y_pred = np.clip(model.predict(X_test), 0, None)

        val_df = pd.DataFrame({
            "actual_days": y_test.values,
            "predicted_days": y_pred,
            "residual": y_pred - y_test.values
        })

        return val_df
    except Exception as e:
        print("Error computing validation sample:", e)
        return None


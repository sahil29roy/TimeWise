"""
Automated tests for TimeWise Combined Parts 4 & 5:
Prediction History and Model Performance backend integrations.
"""

import src.database as db
import src.model_service as ms

def test_prediction_history():
    initial_count = db.get_total_predictions()
    
    # Verify summary metrics
    total = db.get_total_predictions()
    avg = db.get_average_turnaround()
    latest = db.get_latest_prediction()
    
    assert total >= 0, "Total must be non-negative integer"
    if total > 0:
        assert avg is not None, "Average turnaround must not be None when records exist"
        assert latest is not None, "Latest prediction must not be None when records exist"
    
    # Verify reading history does NOT write any documents
    history = db.get_all_predictions(limit=100)
    final_count = db.get_total_predictions()
    assert initial_count == final_count, "Reading history must NEVER insert new documents"
    
    print(f"PASS: Prediction History verified with {total} real MongoDB records.")

def test_model_performance_metrics():
    metrics_data = ms.get_persisted_metrics()
    
    assert metrics_data["selected_model"] == "Random Forest", "Selected model must be Random Forest"
    
    metrics = metrics_data["metrics"]
    assert metrics["MAE"] == 3.41, f"Expected MAE 3.41, got {metrics['MAE']}"
    assert metrics["RMSE"] == 14.91, f"Expected RMSE 14.91, got {metrics['RMSE']}"
    assert metrics["R2"] == -1.552, f"Expected R2 -1.552, got {metrics['R2']}"
    
    comp = metrics_data["models_comparison"]
    assert len(comp) == 4, f"Expected 4 models compared, got {len(comp)}"
    models = [m["model"] for m in comp]
    assert "Baseline (Dummy)" in models
    assert "Linear Regression" in models
    assert "Decision Tree" in models
    assert "Random Forest" in models
    
    val_sample = ms.get_validation_data_sample()
    assert val_sample is not None, "Validation holdout sample must be computed from train.csv"
    assert len(val_sample) == 236, f"Expected 236 validation holdout samples, got {len(val_sample)}"
    assert "actual_days" in val_sample.columns
    assert "predicted_days" in val_sample.columns
    assert "residual" in val_sample.columns
    
    print(f"PASS: Model Performance verified with 4 candidate models and {len(val_sample)} validation samples.")

if __name__ == "__main__":
    test_prediction_history()
    test_model_performance_metrics()
    print("ALL COMBINED PART 4 & 5 TESTS PASSED!")

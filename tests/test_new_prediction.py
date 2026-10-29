"""
Automated tests for TimeWise Part 3: New Prediction page backend and prediction service.
"""

from unittest.mock import patch
from pymongo.errors import PyMongoError
from src.prediction_service import predict_turnaround_time
import src.database as db

def test_prediction_service_valid():
    initial_count = db.get_total_predictions()
    
    # Run genuine prediction
    res = predict_turnaround_time(start_hour=14, start_time="29/10/2026")
    
    assert "predicted_days" in res, "Result must contain predicted_days"
    assert "prediction_id" in res, "Result must contain prediction_id"
    assert isinstance(res["predicted_days"], float), "predicted_days must be a float"
    assert res["prediction_id"] is not None, "prediction_id should be returned when DB is connected"
    
    # Verify exactly ONE record was added to MongoDB
    new_count = db.get_total_predictions()
    assert new_count == initial_count + 1, f"Expected count {initial_count + 1}, got {new_count}"
    
    # Verify record fields in MongoDB
    latest = db.get_latest_prediction()
    assert str(latest["_id"]) == res["prediction_id"], "Latest record ID must match returned prediction_id"
    assert latest["start_hour"] == 14, "Start hour must match input"
    assert latest["start_time"] == "29/10/2026", "Start date must match input"
    print(f"PASS: Valid prediction verified. Predicted days: {res['predicted_days']}, ID: {res['prediction_id']}")

def test_prediction_service_db_offline():
    # Simulate MongoDB offline during save_prediction
    with patch("src.prediction_service.save_prediction", return_value=None):
        res = predict_turnaround_time(start_hour=10, start_time="29/10/2026")
        assert res["predicted_days"] > 0, "Model should still calculate prediction when DB is offline"
        assert res["prediction_id"] is None, "Prediction ID should be None when DB save fails"
        print("PASS: Offline MongoDB handling verified.")

if __name__ == "__main__":
    test_prediction_service_valid()
    test_prediction_service_db_offline()
    print("ALL PART 3 TESTS PASSED!")

"""
Verification test for TimeWise Part 2 Dashboard functionality and backend integration.
"""
from datetime import datetime, date, time
from unittest.mock import patch
from pymongo.errors import PyMongoError
import src.database as db

def test_genuine_metrics():
    total = db.get_total_predictions()
    avg = db.get_average_turnaround()
    latest = db.get_latest_prediction()
    recent = db.get_recent_predictions(5)
    
    assert total == 2, f"Expected total 2, got {total}"
    assert avg == 2.65, f"Expected avg 2.65, got {avg}"
    assert latest is not None, "Latest prediction should not be None"
    assert round(latest["predicted_days"], 2) == 1.11, f"Expected 1.11, got {latest['predicted_days']}"
    assert len(recent) == 2, f"Expected 2 recent predictions, got {len(recent)}"
    print("PASS: Genuine metrics verified.")

def test_date_filter():
    # Filter for today
    today = date(2026, 10, 29)
    start_dt = datetime.combine(today, time.min)
    end_dt = datetime.combine(today, time.max)
    query_today = {"created_at": {"$gte": start_dt, "$lte": end_dt}}
    
    total_today = db.get_total_predictions(query=query_today)
    avg_today = db.get_average_turnaround(query=query_today)
    recent_today = db.get_recent_predictions(limit=5, query=query_today)
    
    assert total_today == 2, f"Expected 2 for today, got {total_today}"
    assert avg_today == 2.65, f"Expected 2.65 for today, got {avg_today}"
    assert len(recent_today) == 2, f"Expected 2 for today, got {len(recent_today)}"
    
    # Filter for past date with no records
    past = date(2026, 10, 1)
    query_past = {"created_at": {"$gte": datetime.combine(past, time.min), "$lte": datetime.combine(past, time.max)}}
    total_past = db.get_total_predictions(query=query_past)
    avg_past = db.get_average_turnaround(query=query_past)
    recent_past = db.get_recent_predictions(limit=5, query=query_past)
    
    assert total_past == 0, f"Expected 0 for past, got {total_past}"
    assert avg_past is None, f"Expected None for past avg, got {avg_past}"
    assert len(recent_past) == 0, f"Expected 0 for past recent, got {len(recent_past)}"
    print("PASS: Date filtering verified.")

def test_mongodb_error_handling():
    with patch.object(db.predictions_collection, "count_documents", side_effect=PyMongoError("Simulated error")):
        assert db.get_total_predictions() == 0, "Should safely return 0 on error"
        
    with patch.object(db.predictions_collection, "find", side_effect=PyMongoError("Simulated error")):
        assert db.get_average_turnaround() is None, "Should safely return None on error"
        assert db.get_all_predictions() == [], "Should safely return empty list on error"
        assert db.get_recent_predictions() == [], "Should safely return empty list on error"
        
    with patch.object(db.predictions_collection, "find_one", side_effect=PyMongoError("Simulated error")):
        assert db.get_latest_prediction() is None, "Should safely return None on error"
        
    print("PASS: MongoDB error handling & graceful fallback verified.")

if __name__ == "__main__":
    test_genuine_metrics()
    test_date_filter()
    test_mongodb_error_handling()
    print("ALL TESTS PASSED!")

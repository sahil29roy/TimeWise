"""
Comprehensive Automated Test Suite for TimeWise Parts 6 & 7 (Phase H)
Testing date parsing, feature preparation, model input compatibility,
prediction service behavior, boundary start-hours, MongoDB operations with mocks,
database error resilience, and duplicate-submission prevention.
"""

import os
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

import joblib
import numpy as np
import pandas as pd
from pymongo.errors import PyMongoError

import src.database as db
from src.prediction_service import predict_turnaround_time
import src.model_service as ms


class TestTimeWiseAppAndModelImprovement(unittest.TestCase):

    def test_date_parsing_and_feature_preparation(self):
        """Verify that date parsing handles mixed formats (with/without seconds) and dayfirst=True."""
        test_strings = [
            "23/05/2013 15:18:29",  # With seconds
            "3/2/2014 10:33",        # Without seconds
            "11/3/2015 10:48",       # Day 11, Month 3
            "29/10/2026",            # Date only
        ]
        parsed = pd.to_datetime(test_strings, format="mixed", dayfirst=True)
        self.assertEqual(parsed.isna().sum(), 0, "All mixed date formats should parse without NaT")
        
        # Verify dayfirst interpretation (3/2/2014 should be Feb 3, 2014)
        self.assertEqual(parsed[1].day, 3)
        self.assertEqual(parsed[1].month, 2)
        self.assertEqual(parsed[1].year, 2014)

        # Verify feature extraction
        start_hour = 14
        input_data = pd.DataFrame([{
            "StartHour": int(start_hour),
            "start_year": parsed[0].year,
            "start_month": parsed[0].month,
            "start_day": parsed[0].day,
            "start_weekday": parsed[0].day_of_week
        }])
        expected_cols = ["StartHour", "start_year", "start_month", "start_day", "start_weekday"]
        self.assertEqual(list(input_data.columns), expected_cols)
        self.assertEqual(input_data["StartHour"].iloc[0], 14)

    def test_model_input_compatibility(self):
        """Verify that both production and experimental models accept the exact 5-feature schema."""
        sample_input = pd.DataFrame([{
            "StartHour": 10,
            "start_year": 2026,
            "start_month": 10,
            "start_day": 29,
            "start_weekday": 3
        }])

        prod_model_path = os.path.join("models", "best_model.joblib")
        self.assertTrue(os.path.exists(prod_model_path), "Production model must exist")
        prod_model = joblib.load(prod_model_path)
        prod_pred = prod_model.predict(sample_input)
        self.assertTrue(np.isscalar(prod_pred[0]) or isinstance(prod_pred[0], (float, np.floating)))

        exp_model_path = os.path.join("models", "experimental_model.joblib")
        if os.path.exists(exp_model_path):
            exp_model = joblib.load(exp_model_path)
            exp_pred = exp_model.predict(sample_input)
            self.assertTrue(np.isscalar(exp_pred[0]) or isinstance(exp_pred[0], (float, np.floating)))

    def test_prediction_service_boundaries(self):
        """Test prediction service with boundary start-hours 0 and 23 using mocks to avoid writing DB records."""
        with patch("src.prediction_service.save_prediction", return_value="mock_pred_id_0"):
            res_0 = predict_turnaround_time(start_hour=0, start_time="29/10/2026")
            self.assertIn("predicted_days", res_0)
            self.assertEqual(res_0["prediction_id"], "mock_pred_id_0")
            self.assertGreaterEqual(res_0["predicted_days"], 0)

        with patch("src.prediction_service.save_prediction", return_value="mock_pred_id_23"):
            res_23 = predict_turnaround_time(start_hour=23, start_time="29/10/2026")
            self.assertIn("predicted_days", res_23)
            self.assertEqual(res_23["prediction_id"], "mock_pred_id_23")
            self.assertGreaterEqual(res_23["predicted_days"], 0)

    def test_mongodb_operations_with_isolated_mocks(self):
        """Verify database read operations return correct aggregates without side effects."""
        mock_docs = [
            {"_id": "id_1", "start_hour": 10, "start_time": "29/10/2026", "predicted_days": 2.0, "created_at": datetime(2026, 10, 29, 10, 0)},
            {"_id": "id_2", "start_hour": 14, "start_time": "29/10/2026", "predicted_days": 4.0, "created_at": datetime(2026, 10, 29, 14, 0)},
        ]
        with patch.object(db.predictions_collection, "count_documents", return_value=len(mock_docs)):
            self.assertEqual(db.get_total_predictions(), 2)

        with patch.object(db.predictions_collection, "find", return_value=iter(mock_docs)):
            avg = db.get_average_turnaround()
            self.assertEqual(avg, 3.0)

    def test_empty_history_and_database_failures(self):
        """Verify that empty collections and database exceptions are handled gracefully without crashing."""
        # Empty collection
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        mock_cursor.__iter__.return_value = iter([])
        with patch.object(db.predictions_collection, "find", return_value=mock_cursor):
            self.assertIsNone(db.get_average_turnaround())
            self.assertEqual(db.get_all_predictions(), [])

        # Simulated PyMongo connection failure
        with patch.object(db.predictions_collection, "count_documents", side_effect=PyMongoError("Simulated outage")):
            self.assertEqual(db.get_total_predictions(), 0)

        with patch.object(db.predictions_collection, "find", side_effect=PyMongoError("Simulated outage")):
            self.assertIsNone(db.get_average_turnaround())
            self.assertEqual(db.get_all_predictions(), [])

        with patch.object(db.predictions_collection, "find_one", side_effect=PyMongoError("Simulated outage")):
            self.assertIsNone(db.get_latest_prediction())

    def test_duplicate_submission_prevention(self):
        """Verify that reading prediction history, filtering, and refreshing never trigger save_prediction."""
        with patch("src.database.save_prediction") as mock_save:
            # Simulate viewing history
            db.get_all_predictions(limit=10)
            db.get_total_predictions()
            db.get_average_turnaround()
            db.get_latest_prediction()
            # Assert save_prediction was never called
            mock_save.assert_not_called()

    def test_saved_model_artifacts_integrity(self):
        """Confirm that saved models and backup artifacts exist and are loadable."""
        self.assertTrue(os.path.exists("models/best_model.joblib"), "Production model must exist")
        self.assertTrue(os.path.exists("models/best_model.joblib.bak"), "Backup model artifact must exist")
        self.assertTrue(os.path.exists("models/experimental_model.joblib"), "Experimental model must exist")
        self.assertTrue(os.path.exists("models/evaluation_metrics.json"), "Evaluation metrics file must exist")

        metrics_data = ms.get_persisted_metrics()
        self.assertIn("models_comparison", metrics_data)
        self.assertIn("production_model", metrics_data)
        self.assertIn("experimental_model", metrics_data)


if __name__ == "__main__":
    unittest.main()

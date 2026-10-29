from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# Connect to local MongoDB
client = MongoClient(
    "mongodb://localhost:27017/",
    serverSelectionTimeoutMS=5000
)

# Select database and collection
db = client["timewise"]
predictions_collection = db["predictions"]


def test_connection():
    try:
        client.admin.command("ping")
        print("MongoDB connected successfully!")
        return True
    except PyMongoError as error:
        print("MongoDB connection failed:", error)
        return False


def save_prediction(start_hour, start_time, predicted_days):
    prediction = {
        "start_hour": int(start_hour),
        "start_time": str(start_time),
        "predicted_days": float(predicted_days),
        "created_at": datetime.now()
    }

    result = predictions_collection.insert_one(prediction)

    return str(result.inserted_id)


def get_prediction_history(limit=10):
    try:
        records = predictions_collection.find().sort(
            "created_at", -1
        ).limit(limit)

        return list(records)
    except (PyMongoError, Exception) as error:
        print("Error retrieving prediction history:", error)
        return []


def get_total_predictions(query=None):
    """Safely return total count of prediction documents."""
    try:
        filter_q = query if query is not None else {}
        return predictions_collection.count_documents(filter_q)
    except (PyMongoError, Exception) as error:
        print("Error counting predictions:", error)
        return 0


def get_average_turnaround(query=None):
    """Safely calculate average predicted turnaround days."""
    try:
        filter_q = query if query is not None else {}
        records = list(predictions_collection.find(filter_q, {"predicted_days": 1}))
        if not records:
            return None
        days = [r["predicted_days"] for r in records if "predicted_days" in r and r["predicted_days"] is not None]
        if not days:
            return None
        return round(sum(days) / len(days), 2)
    except (PyMongoError, Exception) as error:
        print("Error calculating average turnaround:", error)
        return None


def get_latest_prediction():
    """Safely return the most recent prediction document."""
    try:
        return predictions_collection.find_one(sort=[("created_at", -1)])
    except (PyMongoError, Exception) as error:
        print("Error fetching latest prediction:", error)
        return None


def get_all_predictions(limit=100, query=None, sort_ascending=True):
    """Safely return prediction documents for charts and tables."""
    try:
        filter_q = query if query is not None else {}
        sort_order = 1 if sort_ascending else -1
        records = predictions_collection.find(filter_q).sort("created_at", sort_order).limit(limit)
        return list(records)
    except (PyMongoError, Exception) as error:
        print("Error retrieving predictions:", error)
        return []


def get_recent_predictions(limit=5, query=None):
    """Safely return recent predictions sorted by created_at descending."""
    return get_all_predictions(limit=limit, query=query, sort_ascending=False)


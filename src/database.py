
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
    records = predictions_collection.find().sort(
        "created_at", -1
    ).limit(limit)

    return list(records)

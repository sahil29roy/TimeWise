
from src.prediction_service import predict_turnaround_time
from src.database import get_prediction_history

result = predict_turnaround_time(
    start_hour=10,
    start_time="29/10/2026"
)

print("Prediction:", result["predicted_days"], "days")
print("MongoDB ID:", result["prediction_id"])

history = get_prediction_history()
print("Latest saved record:", history[0])

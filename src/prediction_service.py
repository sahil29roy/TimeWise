
import joblib
import pandas as pd

from src.database import save_prediction


# Load the trained model
model = joblib.load("models/best_model.joblib")


def predict_turnaround_time(start_hour, start_time):
    start_time = pd.to_datetime(
        start_time,
        dayfirst=True,
        errors="raise"
    )

    # Prepare features in the same order and format as training
    input_data = pd.DataFrame([{
        "StartHour": int(start_hour),
        "start_year": start_time.year,
        "start_month": start_time.month,
        "start_day": start_time.day,
        "start_weekday": start_time.day_of_week
    }])

    # Get prediction from the trained model
    prediction = float(model.predict(input_data)[0])

    # Save the real prediction in MongoDB
    prediction_id = save_prediction(
        start_hour=start_hour,
        start_time=start_time.strftime("%d/%m/%Y"),
        predicted_days=prediction
    )

    return {
        "predicted_days": round(prediction, 2),
        "prediction_id": prediction_id
    }

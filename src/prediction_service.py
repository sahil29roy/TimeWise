
import joblib
import pandas as pd

# Load the trained model
model = joblib.load("models/best_model.joblib")


def predict_turnaround_time(start_hour, start_time):
    # Convert the input date into datetime format
    start_time = pd.to_datetime(
        start_time,
        dayfirst=True,
        errors="raise"
    )

    # Prepare the input features in the same format as training
    input_data = pd.DataFrame([{
        "StartHour": start_hour,
        "start_year": start_time.year,
        "start_month": start_time.month,
        "start_day": start_time.day,
        "start_weekday": start_time.day_of_week
    }])

    # Get prediction from the model
    prediction = model.predict(input_data)[0]

    return round(float(prediction), 2)

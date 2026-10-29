
from src.database import (
    test_connection,
    save_prediction,
    get_prediction_history
)

if test_connection():
    prediction_id = save_prediction(
        start_hour=10,
        start_time="29/10/2026",
        predicted_days=4.2
    )

    print("Saved prediction ID:", prediction_id)

    history = get_prediction_history()

    print("Records returned:", len(history))

    if history:
        print("Latest prediction:", history[0])

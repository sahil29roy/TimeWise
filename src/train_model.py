import joblib
import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# Load dataset
df = pd.read_csv("data/train.csv")

# Keep only the columns we need
df = df[["StartHour", "Start_Time", "tat_in_days"]].copy()

# Convert date/time column into datetime format
df["Start_Time"] = pd.to_datetime(df["Start_Time"], errors="coerce")

# Extract useful time features
df["start_year"] = df["Start_Time"].dt.year
df["start_month"] = df["Start_Time"].dt.month
df["start_day"] = df["Start_Time"].dt.day
df["start_weekday"] = df["Start_Time"].dt.dayofweek

# Remove rows with missing values
df = df.dropna()

# Select input features and target
X = df[[
    "StartHour",
    "start_year",
    "start_month",
    "start_day",
    "start_weekday"
]]

y = df["tat_in_days"]

# Split data into training and validation sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Models to compare
models = {
    "Baseline": DummyRegressor(strategy="mean"),
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(random_state=42),
    "Random Forest": RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )
}

results = []

# Train and evaluate each model
for name, model in models.items():
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    results.append({
        "Model": name,
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "R2 Score": round(r2, 3)
    })

# Display comparison
results_df = pd.DataFrame(results)
print("\nTimeWise - Model Comparison")
print(results_df.to_string(index=False))

# Best model based on MAE
best_model_name = results_df.loc[
    results_df["MAE"].idxmin(), "Model"
]

print("\nBest model by MAE:", best_model_name)
print("Rows used:", len(df))
print("Training rows:", len(X_train))
print("Validation rows:", len(X_test))


# Train and save the best model
best_model = models[best_model_name]

best_model.fit(X_train, y_train)

# Create models folder if it doesn't exist
os.makedirs("models", exist_ok=True)

# Save the model
joblib.dump(best_model, "models/best_model.joblib")

print("\nBest model saved successfully!")

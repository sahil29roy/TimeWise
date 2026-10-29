"""
Comprehensive Dataset Audit for TimeWise train.csv and test.csv
"""

import pandas as pd
import numpy as np

def run_audit():
    print("=" * 60)
    print("TIMEWISE DATASET AUDIT")
    print("=" * 60)

    # 1. Load train.csv and test.csv
    train_df = pd.read_csv("data/train.csv")
    test_df = pd.read_csv("data/test.csv")

    print(f"\n[1] DATASET SHAPES")
    print(f"train.csv shape: {train_df.shape} (Rows: {train_df.shape[0]}, Cols: {train_df.shape[1]})")
    print(f"test.csv shape:  {test_df.shape} (Rows: {test_df.shape[0]}, Cols: {test_df.shape[1]})")

    print(f"\n[2] COLUMN NAMES & DATA TYPES (train.csv)")
    for col in train_df.columns:
        print(f"  - {col}: {train_df[col].dtype} (nulls: {train_df[col].isna().sum()})")

    print(f"\n[3] DUPLICATES")
    print(f"Exact duplicates across all columns in train: {train_df.duplicated().sum()}")
    print(f"Unique track_id in train: {train_df['track_id'].nunique()} / {len(train_df)}")
    print(f"Duplicate track_id count in train: {train_df['track_id'].duplicated().sum()}")

    print(f"\n[4] TARGET DISTRIBUTION (tat_in_days)")
    target = train_df["tat_in_days"]
    print(f"Count: {target.count()}")
    print(f"Missing: {target.isna().sum()}")
    print(f"Mean: {target.mean():.4f}")
    print(f"Std:  {target.std():.4f}")
    print(f"Min:  {target.min()}")
    print(f"25%:  {target.quantile(0.25)}")
    print(f"50% (Median): {target.median()}")
    print(f"75%:  {target.quantile(0.75)}")
    print(f"90%:  {target.quantile(0.90)}")
    print(f"95%:  {target.quantile(0.95)}")
    print(f"99%:  {target.quantile(0.99)}")
    print(f"Max:  {target.max()}")

    neg_count = (target < 0).sum()
    zero_count = (target == 0).sum()
    gt30_count = (target > 30).sum()
    gt60_count = (target > 60).sum()

    print(f"\nNegative count: {neg_count} ({neg_count / len(target) * 100:.2f}%)")
    print(f"Zero count:     {zero_count} ({zero_count / len(target) * 100:.2f}%)")
    print(f"> 30 days:      {gt30_count} ({gt30_count / len(target) * 100:.2f}%)")
    print(f"> 60 days:      {gt60_count} ({gt60_count / len(target) * 100:.2f}%)")
    print(f"Top 10 highest values: {target.nlargest(10).tolist()}")
    print(f"Top 10 lowest values:  {target.nsmallest(10).tolist()}")

    print(f"\n[5] DATE PARSING INVESTIGATION (Start_Time)")
    sample_dates = train_df["Start_Time"].dropna().head(15).tolist()
    print("Sample raw Start_Time strings:")
    for s in sample_dates:
        print(f"   '{s}'")

    # Check date formats
    # Try parsing with format='%d/%m/%Y' or '%d-%m-%Y' or '%Y-%m-%d'
    # Check failure counts with different approaches:
    p_coerce = pd.to_datetime(train_df["Start_Time"], errors="coerce")
    coerce_fails = p_coerce.isna().sum()
    print(f"\nRaw pd.to_datetime(errors='coerce') failures: {coerce_fails} / {len(train_df)}")

    p_dayfirst = pd.to_datetime(train_df["Start_Time"], errors="coerce", dayfirst=True)
    dayfirst_fails = p_dayfirst.isna().sum()
    print(f"pd.to_datetime(dayfirst=True) failures: {dayfirst_fails} / {len(train_df)}")

    # Check what caused existing dropna:
    # In src/train_model.py:
    # df["Start_Time"] = pd.to_datetime(df["Start_Time"], errors="coerce")
    # df = df.dropna()
    print(f"\n[6] ROWS EXCLUDED BY EXISTING PREPROCESSING (src/train_model.py)")
    existing_df = train_df[["StartHour", "Start_Time", "tat_in_days"]].copy()
    existing_df["parsed_date"] = pd.to_datetime(existing_df["Start_Time"], errors="coerce")
    null_date_count = existing_df["parsed_date"].isna().sum()
    null_hour_count = existing_df["StartHour"].isna().sum()
    null_tat_count = existing_df["tat_in_days"].isna().sum()
    dropped_rows = len(existing_df) - len(existing_df.dropna())
    print(f"Null date strings or unparseable: {null_date_count}")
    print(f"Null StartHour: {null_hour_count}")
    print(f"Null tat_in_days: {null_tat_count}")
    print(f"Total rows dropped by train_model.py: {dropped_rows} out of {len(train_df)} ({dropped_rows/len(train_df)*100:.2f}%)")
    print(f"Rows retained in train_model.py: {len(train_df) - dropped_rows}")

    print(f"\n[7] INSPECTION OF track_id AND ADDITIONAL FEATURES")
    print("Sample track_id values:")
    for tid in train_df["track_id"].head(8):
        print(f"   {tid}")

    # Inspect parts of track_id:
    # Format appears to be: <prefix>-<id>-<origin>-<dest>-<date>-<seq>
    parts = train_df["track_id"].str.split("-", expand=True)
    print("\nSplit track_id component shapes:", parts.shape)
    print("Unique values per component:")
    for col in parts.columns:
        print(f"   Part {col}: {parts[col].nunique()} unique values (samples: {parts[col].dropna().unique()[:4]})")

    print("\n[8] TEST.CSV COMPARISON")
    print("Test columns:", test_df.columns.tolist())
    print("Test nulls:\n", test_df.isna().sum())
    p_test_date = pd.to_datetime(test_df["Start_Time"], errors="coerce", dayfirst=True)
    print(f"Test date parse failures (dayfirst=True): {p_test_date.isna().sum()} / {len(test_df)}")

if __name__ == "__main__":
    run_audit()
